CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY,
    seller_id VARCHAR(36) NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NOT NULL,
    front_image_path VARCHAR(500),
    back_image_path VARCHAR(500),
    flat_lay_image_path VARCHAR(500),
    tech_pack_path VARCHAR(500),
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    extracted_text TEXT,
    validation_summary JSONB,
    chart_summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fabric_specs (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) UNIQUE NOT NULL REFERENCES products(id),
    fabric_type VARCHAR(120) NOT NULL,
    gsm INTEGER,
    stretch_percentage DOUBLE PRECISION,
    weave_type VARCHAR(120),
    shrink_allowance DOUBLE PRECISION,
    stretch_adjustment DOUBLE PRECISION,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS measurements (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id),
    source VARCHAR(64) NOT NULL,
    chest DOUBLE PRECISION NOT NULL,
    waist DOUBLE PRECISION NOT NULL,
    hip DOUBLE PRECISION NOT NULL,
    sleeve DOUBLE PRECISION NOT NULL,
    shoulder DOUBLE PRECISION NOT NULL,
    neck DOUBLE PRECISION NOT NULL,
    length DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generated_size_charts (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) UNIQUE NOT NULL REFERENCES products(id),
    chart_json JSONB NOT NULL,
    explainability_json JSONB NOT NULL,
    validation_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customer_profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    height DOUBLE PRECISION,
    weight DOUBLE PRECISION,
    chest DOUBLE PRECISION,
    waist DOUBLE PRECISION,
    hip DOUBLE PRECISION,
    brand_name VARCHAR(120),
    current_size VARCHAR(16),
    feature_embedding JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL REFERENCES products(id),
    customer_profile_id VARCHAR(36) REFERENCES customer_profiles(id),
    user_id VARCHAR(36) REFERENCES users(id),
    recommended_size VARCHAR(16) NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    explanation_json JSONB NOT NULL,
    request_snapshot_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback (
    id VARCHAR(36) PRIMARY KEY,
    recommendation_id VARCHAR(36) UNIQUE NOT NULL REFERENCES recommendations(id),
    actual_size VARCHAR(16),
    fit_rating INTEGER,
    comments TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
