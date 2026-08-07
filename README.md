# FitWise AI - Dynamic Size & Fit Chart Generator

FitWise AI is a production-oriented hackathon MVP for apparel sizing intelligence. Sellers upload garment assets and a tech pack; the platform extracts measurements, applies fabric rules, generates a graded size chart, and recommends the best size for each customer.

## What is included

- Seller dashboard for uploads and size chart generation
- Customer fit assistant for body measurements or brand-based inputs
- Admin dashboard for validation alerts and sizing trends
- FastAPI backend with JWT authentication and role-based access
- PostgreSQL schema and Redis-backed recommendation cache
- Docker Compose setup for local development
- Mermaid architecture diagram and API documentation

## Local setup

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Start the stack:

```bash
docker-compose up --build
```

3. Open the apps:
- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health

## Demo accounts

- Seller: `seller@fitwise.ai` / `Password123!`
- Customer: `customer@fitwise.ai` / `Password123!`
- Admin: `admin@fitwise.ai` / `Password123!`

## API flow

1. Log in with a demo account to get a JWT token.
2. Paste the token into the Seller, Customer, or Admin page.
3. Upload product assets to generate a size chart.
4. Run the fit assistant to get a recommended size and explanation.
5. Submit feedback to refine future recommendations.

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Notes

- The MVP uses deterministic AI heuristics where datasets or trained models are unavailable.
- The backend never stores raw customer body photos; it stores only structured measurements and feature embeddings.
- Recommendation responses are cached in Redis when available and fall back to in-memory caching otherwise.
