INSERT INTO users (id, email, full_name, hashed_password, role, is_active)
VALUES
  ('11111111-1111-1111-1111-111111111111', 'seller@fitwise.ai', 'FitWise Seller', '$2b$12$u1P3m4Jt4Oa4Yw0v7x1x3e1D4pB0vN8QfYgQm4M2l0A8P3jS4X6Gm', 'seller', true),
  ('22222222-2222-2222-2222-222222222222', 'customer@fitwise.ai', 'FitWise Customer', '$2b$12$u1P3m4Jt4Oa4Yw0v7x1x3e1D4pB0vN8QfYgQm4M2l0A8P3jS4X6Gm', 'customer', true),
  ('33333333-3333-3333-3333-333333333333', 'admin@fitwise.ai', 'FitWise Admin', '$2b$12$u1P3m4Jt4Oa4Yw0v7x1x3e1D4pB0vN8QfYgQm4M2l0A8P3jS4X6Gm', 'admin', true)
ON CONFLICT (email) DO NOTHING;
