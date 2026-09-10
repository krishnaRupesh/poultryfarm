-- ===========================================================================
-- Poultry Farm SQLite Schema DDL with Audit Tables & Triggers
-- ===========================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- 1. PRODUCTS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INT,
    product_name VARCHAR(255),
    price NUMERIC(10, 2),
    date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_products_insert
AFTER INSERT ON products
BEGIN
    INSERT INTO products_audit (
        product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.product_id, NEW.product_name, NEW.price, NEW.date, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_products_update
AFTER UPDATE ON products
BEGIN
    INSERT INTO products_audit (
        product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.product_id, NEW.product_name, NEW.price, NEW.date, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_products_delete
AFTER DELETE ON products
BEGIN
    INSERT INTO products_audit (
        product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.product_id, OLD.product_name, OLD.price, OLD.date, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 2. CUSTOMERS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    address TEXT NOT NULL,
    email_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS customers_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INT,
    customer_name VARCHAR(255),
    phone_number VARCHAR(15),
    address TEXT,
    email_id VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_customers_insert
AFTER INSERT ON customers
BEGIN
    INSERT INTO customers_audit (
        customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.customer_id, NEW.customer_name, NEW.phone_number, NEW.address, NEW.email_id, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_customers_update
AFTER UPDATE ON customers
BEGIN
    INSERT INTO customers_audit (
        customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.customer_id, NEW.customer_name, NEW.phone_number, NEW.address, NEW.email_id, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_customers_delete
AFTER DELETE ON customers
BEGIN
    INSERT INTO customers_audit (
        customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.customer_id, OLD.customer_name, OLD.phone_number, OLD.address, OLD.email_id, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 3. ORDERS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT REFERENCES products(product_id),
    date DATE NOT NULL DEFAULT (CURRENT_DATE),
    price NUMERIC(10, 2) NOT NULL,
    quantity INT NOT NULL,
    discount_price NUMERIC(10, 2),
    remarks TEXT,
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0,
    customer_name VARCHAR(255),
    product_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS orders_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INT,
    customer_id INT,
    product_id INT,
    date DATE,
    price NUMERIC(10, 2),
    quantity INT,
    discount_price NUMERIC(10, 2),
    remarks TEXT,
    total_amount NUMERIC(10, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    customer_name VARCHAR(255),
    product_name VARCHAR(255),
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_orders_insert
AFTER INSERT ON orders
BEGIN
    INSERT INTO orders_audit (
        order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action
    ) VALUES (
        NEW.order_id, NEW.customer_id, NEW.product_id, NEW.date, NEW.price, NEW.quantity, NEW.discount_price, NEW.remarks, NEW.total_amount, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, NEW.product_name, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_orders_update
AFTER UPDATE ON orders
BEGIN
    INSERT INTO orders_audit (
        order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action
    ) VALUES (
        NEW.order_id, NEW.customer_id, NEW.product_id, NEW.date, NEW.price, NEW.quantity, NEW.discount_price, NEW.remarks, NEW.total_amount, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, NEW.product_name, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_orders_delete
AFTER DELETE ON orders
BEGIN
    INSERT INTO orders_audit (
        order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action
    ) VALUES (
        OLD.order_id, OLD.customer_id, OLD.product_id, OLD.date, OLD.price, OLD.quantity, OLD.discount_price, OLD.remarks, OLD.total_amount, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.customer_name, OLD.product_name, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 4. PAYMENTS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INT REFERENCES customers(customer_id),
    payment_amount NUMERIC(10, 2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    payment_mode VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0,
    customer_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS payments_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id INT,
    customer_id INT,
    payment_amount NUMERIC(10, 2),
    payment_date DATE,
    payment_mode VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    customer_name VARCHAR(255),
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_payments_insert
AFTER INSERT ON payments
BEGIN
    INSERT INTO payments_audit (
        payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        NEW.payment_id, NEW.customer_id, NEW.payment_amount, NEW.payment_date, NEW.payment_mode, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_payments_update
AFTER UPDATE ON payments
BEGIN
    INSERT INTO payments_audit (
        payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        NEW.payment_id, NEW.customer_id, NEW.payment_amount, NEW.payment_date, NEW.payment_mode, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_payments_delete
AFTER DELETE ON payments
BEGIN
    INSERT INTO payments_audit (
        payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        OLD.payment_id, OLD.customer_id, OLD.payment_amount, OLD.payment_date, OLD.payment_mode, OLD.remarks, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.customer_name, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 5. INCIDENTS & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    incident_date DATE NOT NULL,
    summary TEXT,
    amount_spent NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS incidents_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INT,
    name VARCHAR(255),
    incident_type VARCHAR(50),
    incident_date DATE,
    summary TEXT,
    amount_spent NUMERIC(10, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_incidents_insert
AFTER INSERT ON incidents
BEGIN
    INSERT INTO incidents_audit (
        incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.incident_id, NEW.name, NEW.incident_type, NEW.incident_date, NEW.summary, NEW.amount_spent, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_incidents_update
AFTER UPDATE ON incidents
BEGIN
    INSERT INTO incidents_audit (
        incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        NEW.incident_id, NEW.name, NEW.incident_type, NEW.incident_date, NEW.summary, NEW.amount_spent, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_incidents_delete
AFTER DELETE ON incidents
BEGIN
    INSERT INTO incidents_audit (
        incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action
    ) VALUES (
        OLD.incident_id, OLD.name, OLD.incident_type, OLD.incident_date, OLD.summary, OLD.amount_spent, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE'
    );
END;

-- ---------------------------------------------------------------------------
-- 6. CUSTOMER BALANCE SUMMARY & AUDIT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customer_balance_summary (
    customer_id INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    remaining_balance NUMERIC(10, 2) NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0,
    customer_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS customer_balance_summary_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INT,
    remaining_balance NUMERIC(10, 2),
    last_updated TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    customer_name VARCHAR(255),
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_customer_balance_summary_insert
AFTER INSERT ON customer_balance_summary
BEGIN
    INSERT INTO customer_balance_summary_audit (
        customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        NEW.customer_id, NEW.remaining_balance, NEW.last_updated, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_customer_balance_summary_update
AFTER UPDATE ON customer_balance_summary
BEGIN
    INSERT INTO customer_balance_summary_audit (
        customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        NEW.customer_id, NEW.remaining_balance, NEW.last_updated, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_customer_balance_summary_delete
AFTER DELETE ON customer_balance_summary
BEGIN
    INSERT INTO customer_balance_summary_audit (
        customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, action
    ) VALUES (
        OLD.customer_id, OLD.remaining_balance, OLD.last_updated, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.customer_name, 'DELETE'
    );
END;
