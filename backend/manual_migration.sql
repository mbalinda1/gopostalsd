-- Manual migration script for pricing models
-- Run this SQL directly in your database

-- Create product_options table
CREATE TABLE IF NOT EXISTS product_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sinalite_option_id INTEGER NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    "group" VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_product_options_product_id ON product_options (product_id);

-- Create product_pricing table
CREATE TABLE IF NOT EXISTS product_pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_code INTEGER NOT NULL,
    option_key VARCHAR(500) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    package_info JSON,
    product_options JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, store_code, option_key)
);

-- Create carts table
CREATE TABLE IF NOT EXISTS carts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id INTEGER,
    store_code INTEGER NOT NULL DEFAULT 6,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create cart_items table
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(255),
    quantity INTEGER NOT NULL DEFAULT 1,
    selected_options JSON NOT NULL,
    option_key VARCHAR(500) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    package_info JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts (id)
);

-- Create shipping_options table
CREATE TABLE IF NOT EXISTS shipping_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    carrier_name VARCHAR(100) NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    shipping_days INTEGER NOT NULL,
    destination_state VARCHAR(10),
    destination_zip VARCHAR(20),
    destination_country VARCHAR(10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts (id)
);

-- Create product_variants table
CREATE TABLE IF NOT EXISTS product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    variant_key VARCHAR(500) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, variant_key)
);

-- Update alembic_version table to reflect the new migration
-- First, check what the current version is
-- Then update it to the new migration ID
-- You can find the migration ID in the migrations/versions/add_pricing_models.py file

-- Example (replace 'add_pricing_models' with the actual revision ID):
-- UPDATE alembic_version SET version_num = 'add_pricing_models' WHERE version_num = 'create_unclassified_product_type';
