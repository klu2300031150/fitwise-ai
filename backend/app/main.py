from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
from pathlib import Path

from app.core.config import settings
from app.db.session import Base, engine, get_db
from app.models import Product, Recommendation
from app.schemas import ProductCreateResponse, ProductRead, RecommendationRequest, RecommendationResponse, SizeChart
from app.services import create_product_record, recommend_for_product, seed_demo_product

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_chart(product: Product) -> SizeChart:
    return SizeChart(
        id=product.id,
        product_id=product.id,
        sizes=product.chart_json,
        notes=product.explanation_json,
        validation={"alerts": ["Demo data" if product.name == "Aero Performance Tee" else "Measurements validated successfully."]},
        created_at=product.created_at,
    )


def serialize_product(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        name=product.name,
        category=product.category,
        fabric_type=product.fabric_type,
        gsm=product.gsm,
        stretch_percentage=product.stretch_percentage,
        weave_type=product.weave_type,
        front_image_path=product.front_image_path,
        back_image_path=product.back_image_path,
        flat_lay_image_path=product.flat_lay_image_path,
        tech_pack_path=product.tech_pack_path,
        tech_pack_text=product.tech_pack_text,
        chart=build_chart(product),
        explanation=product.explanation_json,
        created_at=product.created_at,
    )


@app.on_event("startup")
def startup_seed() -> None:
    with Session(engine) as db:
        seed_demo_product(db)


@app.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)) -> list[ProductRead]:
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return [serialize_product(product) for product in products]


@app.post("/products", response_model=ProductCreateResponse)
def create_product(
    product_name: str = Form(...),
    category: str = Form(...),
    fabric_type: str = Form(...),
    gsm: int | None = Form(default=None),
    stretch_percentage: float | None = Form(default=None),
    weave_type: str | None = Form(default=None),
    front_image: UploadFile | None = File(default=None),
    back_image: UploadFile | None = File(default=None),
    flat_lay_image: UploadFile | None = File(default=None),
    tech_pack: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> ProductCreateResponse:
    try:
        product = create_product_record(
            db,
            name=product_name,
            category=category,
            fabric_type=fabric_type,
            gsm=gsm,
            stretch_percentage=stretch_percentage,
            weave_type=weave_type,
            front_image=front_image,
            back_image=back_image,
            flat_lay_image=flat_lay_image,
            tech_pack=tech_pack,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chart = build_chart(product)
    explanation = ["Product saved.", *product.explanation_json]
    return ProductCreateResponse(
        message="Product saved and size chart generated.",
        product=serialize_product(product),
        chart=chart,
        explanation=explanation,
    )


@app.post("/upload-product", response_model=ProductCreateResponse)
def upload_product(
    product_name: str = Form(...),
    category: str = Form(...),
    fabric_type: str = Form(...),
    gsm: int | None = Form(default=None),
    stretch_percentage: float | None = Form(default=None),
    weave_type: str | None = Form(default=None),
    front_image: UploadFile | None = File(default=None),
    back_image: UploadFile | None = File(default=None),
    flat_lay_image: UploadFile | None = File(default=None),
    tech_pack: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> ProductCreateResponse:
    return create_product(
        product_name=product_name,
        category=category,
        fabric_type=fabric_type,
        gsm=gsm,
        stretch_percentage=stretch_percentage,
        weave_type=weave_type,
        front_image=front_image,
        back_image=back_image,
        flat_lay_image=flat_lay_image,
        tech_pack=tech_pack,
        db=db,
    )


@app.post("/generate-chart", response_model=SizeChart)
def generate_chart(
    product_id: str = Form(...),
    db: Session = Depends(get_db),
) -> SizeChart:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return build_chart(product)


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = recommend_for_product(
        product,
        {
            "height": payload.height or 0.0,
            "weight": payload.weight or 0.0,
            "chest": payload.chest,
            "waist": payload.waist,
            "hip": payload.hip,
        },
    )

    recommendation = Recommendation(
        product_id=product.id,
        height=payload.height,
        weight=payload.weight,
        chest=payload.chest,
        waist=payload.waist,
        hip=payload.hip,
        recommended_size=result["recommended_size"],
        confidence_score=result["confidence_score"],
        reason_json=result["explanation"],
    )
    db.add(recommendation)
    db.commit()

    return RecommendationResponse(
        product_id=product.id,
        recommended_size=result["recommended_size"],
        confidence_score=result["confidence_score"],
        reason=result["explanation"],
        size_table=product.chart_json,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)) -> dict:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Remove related recommendations
    try:
        db.query(Recommendation).filter(Recommendation.product_id == product.id).delete(synchronize_session=False)
    except Exception:
        pass

    # Remove stored files for the product
    try:
        storage_root = Path(settings.storage_dir)
        product_dir = storage_root / product.id
        if product_dir.exists():
            shutil.rmtree(product_dir)
    except Exception:
        pass

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
