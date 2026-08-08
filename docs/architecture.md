# Architecture

```mermaid
graph TD
    subgraph Frontend
        A[Seller / Customer]
        B[React + Vite UI]
    end

    subgraph Authentication
        J[JWT Authentication]
    end

    subgraph Backend
        C[FastAPI REST API]
        C -->|stores users, products, measurements, charts, recommendations| P[PostgreSQL]
        C -->|caches frequent results| R[Redis Cache]
        C -->|handles uploads + file processing| U[PDF/Image Upload & Processing]
        C -->|uses AI insights| AI[AI Processing / Recommendation Engine]
    end

    subgraph AI_Layer[AI Processing / Recommendation Engine]
        CV[Computer Vision]
        OCR[OCR]
        NLP[NLP]
        BAY[Bayesian Recommendation Model]
        RULE[Rule-Based AI]
    end

    subgraph Output
        S[Size / Fit Recommendation]
        SC[Size Chart Generation]
    end

    subgraph Deployment
        DC[Docker Compose]
    end

    A --> B
    B --> J
    J --> C
    C --> AI
    AI --> S
    OCR --> SC
    AI --> SC
    U --> OCR
    C --> SC
    DC --> C
    DC --> P
    DC --> R
    DC --> AI
    DC --> U
```

This architecture shows:

- Frontend: Seller / Customer access via a React + Vite UI.
- Authentication: JWT Authentication between the frontend and FastAPI backend.
- Backend: FastAPI REST API as the central service.
- Database: PostgreSQL storing users, measurements, seller/product data, size charts, and recommendation-related data.
- Cache: Redis Cache connected to FastAPI for frequently accessed data and results.
- AI Processing Layer: Computer Vision, OCR, NLP, Bayesian Recommendation Model, and Rule-Based AI.
- File / Upload Processing: PDF/Image upload and text extraction connected to OCR and the backend.
- Size Chart Generation: linked to OCR/AI processing and FastAPI.
- Deployment: Docker Compose orchestrating FastAPI, PostgreSQL, Redis, and AI services.
