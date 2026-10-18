-- ===========================================================================
-- BigQuery Schema DDL for Poultry Farm Management & Finance
-- Google Standard SQL Dialect
-- Dataset default: poultry_farm
-- ===========================================================================

-- 1. PRODUCTS
CREATE TABLE IF NOT EXISTS `poultry_farm.products` (
    product_id INT64 NOT NULL,
    product_name STRING NOT NULL,
    price NUMERIC NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
PARTITION BY date
CLUSTER BY product_name;

-- 2. CUSTOMERS
CREATE TABLE IF NOT EXISTS `poultry_farm.customers` (
    customer_id INT64 NOT NULL,
    customer_name STRING NOT NULL,
    phone_number STRING NOT NULL,
    address STRING NOT NULL,
    email_id STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
CLUSTER BY customer_name;

-- 3. ORDERS
CREATE TABLE IF NOT EXISTS `poultry_farm.orders` (
    order_id INT64 NOT NULL,
    customer_id INT64 NOT NULL,
    product_id INT64 NOT NULL,
    date DATE NOT NULL,
    price NUMERIC NOT NULL,
    quantity INT64 NOT NULL,
    discount_price NUMERIC,
    remarks STRING,
    total_amount NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
PARTITION BY date
CLUSTER BY customer_id, product_id;

-- 4. PAYMENTS
CREATE TABLE IF NOT EXISTS `poultry_farm.payments` (
    payment_id INT64 NOT NULL,
    customer_id INT64 NOT NULL,
    payment_amount NUMERIC NOT NULL,
    payment_date DATE NOT NULL,
    payment_mode STRING,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
PARTITION BY payment_date
CLUSTER BY customer_id;

-- 5. INCIDENTS
CREATE TABLE IF NOT EXISTS `poultry_farm.incidents` (
    incident_id INT64 NOT NULL,
    name STRING NOT NULL,
    incident_type STRING NOT NULL,
    incident_date DATE NOT NULL,
    summary STRING,
    amount_spent NUMERIC NOT NULL,
    shed_id INT64,
    batch_id INT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
PARTITION BY incident_date
CLUSTER BY incident_type;

-- 5A. SHEDS
CREATE TABLE IF NOT EXISTS `poultry_farm.sheds` (
    shed_id INT64 NOT NULL,
    shed_name STRING NOT NULL,
    capacity INT64 NOT NULL,
    shed_type STRING DEFAULT 'Layer',
    status STRING DEFAULT 'Active',
    location STRING,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
CLUSTER BY status;

-- 5B. FLOCK BATCHES
CREATE TABLE IF NOT EXISTS `poultry_farm.flock_batches` (
    batch_id INT64 NOT NULL,
    batch_name STRING NOT NULL,
    shed_id INT64,
    breed STRING DEFAULT 'Layer (BV300)',
    bird_type STRING DEFAULT 'Layer',
    placement_date DATE NOT NULL,
    initial_birds INT64 NOT NULL,
    current_birds INT64 NOT NULL,
    initial_age_weeks INT64 DEFAULT 18,
    status STRING DEFAULT 'Active',
    depletion_date DATE,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
PARTITION BY placement_date
CLUSTER BY shed_id, status;

-- 6. CUSTOMER BALANCE SUMMARY
CREATE TABLE IF NOT EXISTS `poultry_farm.customer_balance_summary` (
    customer_id INT64 NOT NULL,
    customer_name STRING,
    remaining_balance NUMERIC NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
CLUSTER BY customer_id;

-- ---------------------------------------------------------------------------
-- 7. FEED INVENTORY & OPERATIONS
-- ---------------------------------------------------------------------------

-- FEED ITEMS
CREATE TABLE IF NOT EXISTS `poultry_farm.feed_items` (
    item_id INT64 NOT NULL,
    name STRING NOT NULL,
    category STRING,
    default_unit STRING DEFAULT 'kg',
    current_stock_kg NUMERIC DEFAULT 0.0,
    average_cost_per_kg NUMERIC DEFAULT 0.0,
    reorder_level_kg NUMERIC DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
CLUSTER BY category;

-- FEED PURCHASES
CREATE TABLE IF NOT EXISTS `poultry_farm.feed_purchases` (
    purchase_id INT64 NOT NULL,
    item_id INT64 NOT NULL,
    purchase_date DATE NOT NULL,
    quantity_kg NUMERIC NOT NULL,
    cost_per_kg NUMERIC NOT NULL,
    total_cost NUMERIC NOT NULL,
    vendor_name STRING,
    invoice_no STRING,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE
)
PARTITION BY purchase_date
CLUSTER BY item_id;

-- DAILY FLOCK STATUS
CREATE TABLE IF NOT EXISTS `poultry_farm.daily_flock_status` (
    status_id INT64 NOT NULL,
    date DATE NOT NULL,
    shed_id INT64,
    batch_id INT64,
    active_birds INT64 NOT NULL,
    mortality INT64 DEFAULT 0,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
PARTITION BY date
CLUSTER BY shed_id, batch_id;

-- DAILY FEED CONSUMPTION
CREATE TABLE IF NOT EXISTS `poultry_farm.daily_feed_consumption` (
    consumption_id INT64 NOT NULL,
    date DATE NOT NULL,
    item_id INT64 NOT NULL,
    shed_id INT64,
    batch_id INT64,
    quantity_kg NUMERIC NOT NULL,
    cost_per_kg NUMERIC NOT NULL,
    total_cost NUMERIC NOT NULL,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
PARTITION BY date
CLUSTER BY item_id, batch_id;

-- DAILY EGG OPERATIONS
CREATE TABLE IF NOT EXISTS `poultry_farm.daily_egg_operations` (
    record_id INT64 NOT NULL,
    date DATE NOT NULL,
    shed_id INT64,
    batch_id INT64,
    opening_stock INT64 DEFAULT 0,
    eggs_produced INT64 NOT NULL,
    damaged_eggs INT64 DEFAULT 0,
    eggs_available INT64 NOT NULL,
    eggs_sold INT64 DEFAULT 0,
    closing_stock INT64 NOT NULL,
    egg_price_per_unit NUMERIC NOT NULL,
    actual_revenue NUMERIC NOT NULL,
    remarks STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING NOT NULL,
    updated_by STRING,
    is_deleted BOOL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
PARTITION BY date
CLUSTER BY shed_id, batch_id;

-- ---------------------------------------------------------------------------
-- 8. BIGQUERY ANALYTICAL VIEW: DAILY COST & PROFITABILITY SUMMARY
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW `poultry_farm.v_daily_cost_and_profitability_summary` AS
WITH feed_summary AS (
    SELECT
        date,
        SUM(quantity_kg) AS total_feed_kg,
        ROUND(SUM(quantity_kg) / 1000.0, 3) AS total_feed_mt,
        ROUND(SUM(total_cost), 2) AS total_feed_cost
    FROM `poultry_farm.daily_feed_consumption`
    WHERE is_deleted = FALSE
    GROUP BY date
),
flock_summary AS (
    SELECT
        date,
        active_birds,
        mortality
    FROM `poultry_farm.daily_flock_status`
    WHERE is_deleted = FALSE
),
egg_summary AS (
    SELECT
        date,
        opening_stock,
        eggs_produced,
        damaged_eggs,
        eggs_available,
        eggs_sold,
        closing_stock,
        egg_price_per_unit,
        actual_revenue
    FROM `poultry_farm.daily_egg_operations`
    WHERE is_deleted = FALSE
)
SELECT
    COALESCE(e.date, f.date, fl.date) AS date,
    COALESCE(fl.active_birds, 0) AS active_birds,
    COALESCE(fl.mortality, 0) AS mortality,
    COALESCE(f.total_feed_mt, 0.0) AS total_feed_mt,
    COALESCE(f.total_feed_kg, 0.0) AS total_feed_kg,
    COALESCE(f.total_feed_cost, 0.0) AS total_feed_cost,
    ROUND(SAFE_DIVIDE(f.total_feed_cost, fl.active_birds), 4) AS feed_cost_per_bird,
    ROUND(SAFE_DIVIDE(f.total_feed_kg * 1000.0, fl.active_birds), 1) AS feed_grams_per_bird,
    COALESCE(e.eggs_produced, 0) AS eggs_produced,
    ROUND(SAFE_DIVIDE(e.eggs_produced * 100.0, fl.active_birds), 2) AS laying_percentage,
    ROUND(SAFE_DIVIDE(f.total_feed_cost, e.eggs_produced), 4) AS production_cost_per_egg,
    COALESCE(e.egg_price_per_unit, 0.0) AS egg_price_per_unit,
    ROUND(e.egg_price_per_unit - SAFE_DIVIDE(f.total_feed_cost, e.eggs_produced), 4) AS profit_margin_per_egg,
    COALESCE(e.eggs_sold, 0) AS eggs_sold,
    COALESCE(e.actual_revenue, 0.0) AS actual_revenue,
    ROUND(e.eggs_sold * (e.egg_price_per_unit - SAFE_DIVIDE(f.total_feed_cost, e.eggs_produced)), 2) AS realized_gross_profit,
    COALESCE(e.closing_stock, 0) AS closing_unsold_stock,
    ROUND(e.closing_stock * SAFE_DIVIDE(f.total_feed_cost, e.eggs_produced), 2) AS unsold_inventory_value
FROM egg_summary e
FULL OUTER JOIN feed_summary f ON e.date = f.date
FULL OUTER JOIN flock_summary fl ON COALESCE(e.date, f.date) = fl.date
ORDER BY date DESC;
