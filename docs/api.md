# API Documentation

## Product and chart flow

- `GET /products` returns the stored products and generated charts.
- `POST /products` uploads product details and generates a size chart.

## Fit assistant

- `POST /recommend` compares customer measurements with the stored product chart and returns a recommended size.

## Notes

- No authentication is required in this simplified MVP.
- A seeded demo product is created on backend startup.
