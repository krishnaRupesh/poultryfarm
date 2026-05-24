CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE products_audit (
    audit_id SERIAL PRIMARY KEY,
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

CREATE OR REPLACE FUNCTION products_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO products_audit (product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.product_id, NEW.product_name, NEW.price, NEW.date, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO products_audit (product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.product_id, NEW.product_name, NEW.price, NEW.date, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO products_audit (product_id, product_name, price, date, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (OLD.product_id, OLD.product_name, OLD.price, OLD.date, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW EXECUTE FUNCTION products_audit_trigger_function();
