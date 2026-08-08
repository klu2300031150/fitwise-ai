# FitWise AI - Dynamic Size & Fit Chart Generator

FitWise AI is a simplified MVP for apparel sizing intelligence. Sellers upload garment details and a tech pack, the backend generates a size chart, and customers get a size recommendation from a rule-based fit engine.

## What is included

- Home page
- Seller dashboard for product upload and chart generation
- Customer fit assistant for measurement-based recommendations
- FastAPI backend with SQLite storage
- Docker Compose with backend and frontend containers only
- Rule-based size chart and recommendation engine

## Local setup

1. Copy `.env.example` to `.env` if needed.
2. Start the stack:

```bash
docker compose up --build
```

3. Open the app:
- Frontend: http://localhost:5173

## Notes

- A demo product is seeded on backend startup so the customer assistant works immediately.
- There is no authentication, Redis, or PostgreSQL required for this MVP.
- Upload a product from the seller dashboard and then use the customer assistant to get a recommended size.
