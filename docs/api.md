# API Documentation

## Authentication

- `POST /auth/register` creates a new user.
- `POST /auth/login` returns a JWT bearer token.
- `GET /me` returns the current authenticated user.

## Product and chart flow

- `POST /upload-product` uploads images, a tech pack, and fabric metadata.
- `POST /generate-chart` regenerates a chart for an existing product.
- `GET /product/{id}` returns stored product metadata.
- `GET /chart/{id}` returns the generated chart.

## Fit assistant

- `POST /recommend-size` compares customer measurements or brand preference with the chart.
- `POST /feedback` stores fit feedback for future confidence tuning.

## Admin

- `GET /admin/summary` returns operational metrics, validation alerts, and sizing trends.

## Demo accounts

- `seller@fitwise.ai / Password123!`
- `customer@fitwise.ai / Password123!`
- `admin@fitwise.ai / Password123!`
