-- ===========================================================================
-- Feed Inventory, Flock, Feeding, and Egg Operations DDL (SQLite & Postgres compatible)
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- 7. FEED ITEMS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feed_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    default_unit VARCHAR(20) DEFAULT 'kg',
    current_stock_kg NUMERIC(12, 2) DEFAULT 0.0,
    average_cost_per_kg NUMERIC(10, 4) DEFAULT 0.0,
    reorder_level_kg NUMERIC(10, 2) DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feed_items_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INT,
    name VARCHAR(255),
    category VARCHAR(100),
    default_unit VARCHAR(20),
    current_stock_kg NUMERIC(12, 2),
    average_cost_per_kg NUMERIC(10, 4),
    reorder_level_kg NUMERIC(10, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_feed_items_insert
AFTER INSERT ON feed_items
BEGIN
    INSERT INTO feed_items_audit (
        item_id, name, category, default_unit, current_stock_kg, average_cost_per_kg,
        reorder_level_kg, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.item_id, NEW.name, NEW.category, NEW.default_unit, NEW.current_stock_kg,
        NEW.average_cost_per_kg, NEW.reorder_level_kg, NEW.created_at, NEW.updated_at,
        NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_feed_items_update
AFTER UPDATE ON feed_items
BEGIN
    INSERT INTO feed_items_audit (
        item_id, name, category, default_unit, current_stock_kg, average_cost_per_kg,
        reorder_level_kg, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.item_id, NEW.name, NEW.category, NEW.default_unit, NEW.current_stock_kg,
        NEW.average_cost_per_kg, NEW.reorder_level_kg, NEW.created_at, NEW.updated_at,
        NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_feed_items_delete
AFTER DELETE ON feed_items
BEGIN
    INSERT INTO feed_items_audit (
        item_id, name, category, default_unit, current_stock_kg, average_cost_per_kg,
        reorder_level_kg, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.item_id, OLD.name, OLD.category, OLD.default_unit, OLD.current_stock_kg,
        OLD.average_cost_per_kg, OLD.reorder_level_kg, OLD.created_at, OLD.updated_at,
        OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 8. FEED PURCHASES & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feed_purchases (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES feed_items(item_id),
    purchase_date DATE NOT NULL,
    quantity_kg NUMERIC(12, 2) NOT NULL,
    cost_per_kg NUMERIC(10, 4) NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL,
    vendor_name VARCHAR(255),
    invoice_no VARCHAR(100),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feed_purchases_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INT,
    item_id INT,
    purchase_date DATE,
    quantity_kg NUMERIC(12, 2),
    cost_per_kg NUMERIC(10, 4),
    total_cost NUMERIC(12, 2),
    vendor_name VARCHAR(255),
    invoice_no VARCHAR(100),
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_feed_purchases_insert
AFTER INSERT ON feed_purchases
BEGIN
    INSERT INTO feed_purchases_audit (
        purchase_id, item_id, purchase_date, quantity_kg, cost_per_kg, total_cost,
        vendor_name, invoice_no, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.purchase_id, NEW.item_id, NEW.purchase_date, NEW.quantity_kg, NEW.cost_per_kg, NEW.total_cost,
        NEW.vendor_name, NEW.invoice_no, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_feed_purchases_update
AFTER UPDATE ON feed_purchases
BEGIN
    INSERT INTO feed_purchases_audit (
        purchase_id, item_id, purchase_date, quantity_kg, cost_per_kg, total_cost,
        vendor_name, invoice_no, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.purchase_id, NEW.item_id, NEW.purchase_date, NEW.quantity_kg, NEW.cost_per_kg, NEW.total_cost,
        NEW.vendor_name, NEW.invoice_no, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_feed_purchases_delete
AFTER DELETE ON feed_purchases
BEGIN
    INSERT INTO feed_purchases_audit (
        purchase_id, item_id, purchase_date, quantity_kg, cost_per_kg, total_cost,
        vendor_name, invoice_no, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.purchase_id, OLD.item_id, OLD.purchase_date, OLD.quantity_kg, OLD.cost_per_kg, OLD.total_cost,
        OLD.vendor_name, OLD.invoice_no, OLD.remarks, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 9. DAILY FLOCK STATUS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_flock_status (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    active_birds INTEGER NOT NULL,
    mortality INTEGER DEFAULT 0,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_flock_status_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_id INT,
    date DATE,
    active_birds INT,
    mortality INT,
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_daily_flock_status_insert
AFTER INSERT ON daily_flock_status
BEGIN
    INSERT INTO daily_flock_status_audit (
        status_id, date, active_birds, mortality, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.status_id, NEW.date, NEW.active_birds, NEW.mortality, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_flock_status_update
AFTER UPDATE ON daily_flock_status
BEGIN
    INSERT INTO daily_flock_status_audit (
        status_id, date, active_birds, mortality, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.status_id, NEW.date, NEW.active_birds, NEW.mortality, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_flock_status_delete
AFTER DELETE ON daily_flock_status
BEGIN
    INSERT INTO daily_flock_status_audit (
        status_id, date, active_birds, mortality, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.status_id, OLD.date, OLD.active_birds, OLD.mortality, OLD.remarks,
        OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 10. DAILY FEED CONSUMPTION & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_feed_consumption (
    consumption_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    item_id INTEGER NOT NULL REFERENCES feed_items(item_id),
    quantity_kg NUMERIC(12, 2) NOT NULL,
    cost_per_kg NUMERIC(10, 4) NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_feed_consumption_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    consumption_id INT,
    date DATE,
    item_id INT,
    quantity_kg NUMERIC(12, 2),
    cost_per_kg NUMERIC(10, 4),
    total_cost NUMERIC(12, 2),
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_daily_feed_consumption_insert
AFTER INSERT ON daily_feed_consumption
BEGIN
    INSERT INTO daily_feed_consumption_audit (
        consumption_id, date, item_id, quantity_kg, cost_per_kg, total_cost, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.consumption_id, NEW.date, NEW.item_id, NEW.quantity_kg, NEW.cost_per_kg, NEW.total_cost, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_feed_consumption_update
AFTER UPDATE ON daily_feed_consumption
BEGIN
    INSERT INTO daily_feed_consumption_audit (
        consumption_id, date, item_id, quantity_kg, cost_per_kg, total_cost, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.consumption_id, NEW.date, NEW.item_id, NEW.quantity_kg, NEW.cost_per_kg, NEW.total_cost, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_feed_consumption_delete
AFTER DELETE ON daily_feed_consumption
BEGIN
    INSERT INTO daily_feed_consumption_audit (
        consumption_id, date, item_id, quantity_kg, cost_per_kg, total_cost, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.consumption_id, OLD.date, OLD.item_id, OLD.quantity_kg, OLD.cost_per_kg, OLD.total_cost, OLD.remarks,
        OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 11. DAILY EGG OPERATIONS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_egg_operations (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    opening_stock INTEGER DEFAULT 0,
    eggs_produced INTEGER NOT NULL,
    damaged_eggs INTEGER DEFAULT 0,
    eggs_available INTEGER NOT NULL,
    eggs_sold INTEGER NOT NULL DEFAULT 0,
    closing_stock INTEGER NOT NULL,
    egg_price_per_unit NUMERIC(10, 2) NOT NULL,
    actual_revenue NUMERIC(12, 2) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_egg_operations_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INT,
    date DATE,
    opening_stock INT,
    eggs_produced INT,
    damaged_eggs INT,
    eggs_available INT,
    eggs_sold INT,
    closing_stock INT,
    egg_price_per_unit NUMERIC(10, 2),
    actual_revenue NUMERIC(12, 2),
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_daily_egg_operations_insert
AFTER INSERT ON daily_egg_operations
BEGIN
    INSERT INTO daily_egg_operations_audit (
        record_id, date, opening_stock, eggs_produced, damaged_eggs,
        eggs_available, eggs_sold, closing_stock, egg_price_per_unit, actual_revenue, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.record_id, NEW.date, NEW.opening_stock, NEW.eggs_produced, NEW.damaged_eggs,
        NEW.eggs_available, NEW.eggs_sold, NEW.closing_stock, NEW.egg_price_per_unit, NEW.actual_revenue, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_egg_operations_update
AFTER UPDATE ON daily_egg_operations
BEGIN
    INSERT INTO daily_egg_operations_audit (
        record_id, date, opening_stock, eggs_produced, damaged_eggs,
        eggs_available, eggs_sold, closing_stock, egg_price_per_unit, actual_revenue, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.record_id, NEW.date, NEW.opening_stock, NEW.eggs_produced, NEW.damaged_eggs,
        NEW.eggs_available, NEW.eggs_sold, NEW.closing_stock, NEW.egg_price_per_unit, NEW.actual_revenue, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_daily_egg_operations_delete
AFTER DELETE ON daily_egg_operations
BEGIN
    INSERT INTO daily_egg_operations_audit (
        record_id, date, opening_stock, eggs_produced, damaged_eggs,
        eggs_available, eggs_sold, closing_stock, egg_price_per_unit, actual_revenue, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.record_id, OLD.date, OLD.opening_stock, OLD.eggs_produced, OLD.damaged_eggs,
        OLD.eggs_available, OLD.eggs_sold, OLD.closing_stock, OLD.egg_price_per_unit, OLD.actual_revenue, OLD.remarks,
        OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;
