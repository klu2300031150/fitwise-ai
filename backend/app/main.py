from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_current_user, hash_password, require_role, verify_password
from app.cache import RecommendationCache
from app.db.session import Base, engine, get_db
from app.models import CustomerProfile, Feedback, GeneratedSizeChart, Measurement, Product, Recommendation, User
from app.schemas import (
    AdminSummary,
    BodyMeasurements,
    BrandSelection,
    ChartRequest,
    ChartResponse,
    CustomerFitInput,
    FeedbackCreate,
    FeedbackRead,
    LoginRequest,
    ProductRead,
    ProductUploadResponse,
    RecommendationResponse,
    SizeChart,
    Token,
    UploadSummary,
    UserCreate,
    UserRead,
)
from app.services import create_product_and_chart, generate_recommendation, regenerate_chart_for_product, recommendation_cache_key, upsert_customer_profile

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_product(product: Product) -> ProductRead:
    return ProductRead.model_validate(product)


def serialize_chart(chart: GeneratedSizeChart) -> SizeChart:
    return SizeChart(
        id=chart.id,
        product_id=chart.product_id,
        sizes=chart.chart_json,
        notes=chart.explainability_json.get("notes", []),
        validation=chart.validation_json,
        created_at=chart.created_at,
    )


def get_product_or_404(db: Session, product_id: str) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@app.on_event("startup")
def startup_seed() -> None:
    from sqlalchemy.orm import Session as SQLASession

    db = SQLASession(bind=engine)
    try:
        app.state.cache = RecommendationCache(settings.redis_url)
        demo_users = [
            ("seller@fitwise.ai", "FitWise Seller", "seller"),
            ("customer@fitwise.ai", "FitWise Customer", "customer"),
            ("admin@fitwise.ai", "FitWise Admin", "admin"),
        ]
        for email, full_name, role in demo_users:
            existing = db.query(User).filter(User.email == email).one_or_none()
            if not existing:
                db.add(User(email=email, full_name=full_name, role=role, hashed_password=hash_password("Password123!")))
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/auth/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@app.post("/auth/login", response_model=Token)
def login_user(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = db.query(User).filter(User.email == form_data.username).one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=token)


@app.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@app.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ProductRead]:
    query = db.query(Product)
    if current_user.role == "seller":
        query = query.filter(Product.seller_id == current_user.id)
    products = query.order_by(Product.created_at.desc()).all()
    return [serialize_product(product) for product in products]


@app.get("/product/{product_id}", response_model=ProductRead)
def get_product(product_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ProductRead:
    product = get_product_or_404(db, product_id)
    if current_user.role == "seller" and product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your product")
    return serialize_product(product)


@app.get("/chart/{product_id}", response_model=ChartResponse)
def get_chart(product_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ChartResponse:
    product = get_product_or_404(db, product_id)
    chart = product.generated_chart
    if not chart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not generated yet")
    return ChartResponse(chart=serialize_chart(chart))


@app.post("/upload-product", response_model=ProductUploadResponse)
def upload_product(
    product_name: str = Form(...),
    product_category: str = Form(...),
    fabric_type: str = Form(...),
    gsm: int | None = Form(default=None),
    stretch_percentage: float | None = Form(default=None),
    weave_type: str | None = Form(default=None),
    front_image: UploadFile | None = File(default=None),
    back_image: UploadFile | None = File(default=None),
    flat_lay_image: UploadFile | None = File(default=None),
    tech_pack: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("seller", "admin")),
) -> ProductUploadResponse:
    try:
        product, chart, summary = create_product_and_chart(
            db=db,
            seller=current_user,
            name=product_name,
            category=product_category,
            front_image=front_image,
            back_image=back_image,
            flat_lay_image=flat_lay_image,
            tech_pack=tech_pack,
            fabric_type=fabric_type,
            gsm=gsm,
            stretch_percentage=stretch_percentage,
            weave_type=weave_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProductUploadResponse(
        product=serialize_product(product),
        fabric={
            "fabric_type": summary["fabric"]["fabric_type"],
            "gsm": summary["fabric"].get("gsm"),
            "stretch_percentage": summary["fabric"].get("stretch_percentage"),
            "weave_type": summary["fabric"].get("weave_type"),
        },
        measurements=summary["baseline"],
        chart=serialize_chart(chart),
        explainability=summary,
    )


@app.post("/generate-chart", response_model=ChartResponse)
def generate_chart(
    payload: ChartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("seller", "admin")),
) -> ChartResponse:
    product = get_product_or_404(db, payload.product_id)
    if current_user.role == "seller" and product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your product")
    try:
        chart = regenerate_chart_for_product(db, product)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ChartResponse(chart=serialize_chart(chart))


@app.post("/recommend-size", response_model=RecommendationResponse)
def recommend(
    payload: CustomerFitInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    product = get_product_or_404(db, payload.product_id)
    if not product.generated_chart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generate the size chart first")
    raw_payload = payload.model_dump()
    cache_key = recommendation_cache_key(product.id, raw_payload)
    cache_hit = False
    recommendation_result: dict[str, Any] | None = None
    cached = getattr(app.state, "cache", None)
    if cached is not None:
        recommendation_result = cached.get(cache_key)
        cache_hit = recommendation_result is not None
    if not recommendation_result:
        customer_profile = upsert_customer_profile(db, raw_payload)
        recommended_size, confidence_score, explanation, size_table = generate_recommendation(db, product, raw_payload)
        recommendation_result = {
            "recommendation_id": None,
            "product_id": product.id,
            "recommended_size": recommended_size,
            "confidence_score": confidence_score,
            "explanation": explanation,
            "size_table": size_table,
        }
        if cached is not None:
            cached.set(cache_key, recommendation_result)
    else:
        customer_profile = upsert_customer_profile(db, raw_payload)
        recommendation_result = {**recommendation_result, "cache_hit": True}

    recommendation = Recommendation(
        product_id=product.id,
        customer_profile_id=customer_profile.id,
        user_id=current_user.id,
        recommended_size=recommendation_result["recommended_size"],
        confidence_score=recommendation_result["confidence_score"],
        explanation_json={"items": recommendation_result["explanation"]},
        request_snapshot_json={**raw_payload, "cache_hit": cache_hit},
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    recommendation_result["recommendation_id"] = recommendation.id
    if cached is not None and not cache_hit:
        cached.set(cache_key, recommendation_result)
    return RecommendationResponse(
        recommendation_id=recommendation.id,
        product_id=product.id,
        recommended_size=recommendation_result["recommended_size"],
        confidence_score=recommendation_result["confidence_score"],
        explanation=recommendation_result["explanation"],
        cache_hit=cache_hit,
        size_table=recommendation_result.get("size_table", []),
    )


@app.post("/feedback", response_model=FeedbackRead)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackRead:
    recommendation = db.get(Recommendation, payload.recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    feedback = Feedback(
        recommendation_id=recommendation.id,
        actual_size=payload.actual_size,
        fit_rating=payload.fit_rating,
        comments=payload.comments,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return FeedbackRead.model_validate(feedback)


@app.get("/admin/summary", response_model=AdminSummary)
def get_admin_summary(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))) -> AdminSummary:
    from app.services import admin_summary

    summary = admin_summary(db)
    return AdminSummary(**summary)


@app.get("/demo/credentials")
def demo_credentials() -> dict[str, list[dict[str, str]]]:
    return {
        "accounts": [
            {"email": "seller@fitwise.ai", "password": "Password123!", "role": "seller"},
            {"email": "customer@fitwise.ai", "password": "Password123!", "role": "customer"},
            {"email": "admin@fitwise.ai", "password": "Password123!", "role": "admin"},
        ]
    }
