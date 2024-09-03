CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    address TEXT NOT NULL,
    email_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE customers_audit (
    audit_id SERIAL PRIMARY KEY,
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
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION customers_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO customers_audit (customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.customer_id, NEW.customer_name, NEW.phone_number, NEW.address, NEW.email_id, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO customers_audit (customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.customer_id, NEW.customer_name, NEW.phone_number, NEW.address, NEW.email_id, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO customers_audit (customer_id, customer_name, phone_number, address, email_id, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (OLD.customer_id, OLD.customer_name, OLD.phone_number, OLD.address, OLD.email_id, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER customers_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON customers
FOR EACH ROW EXECUTE FUNCTION customers_audit_trigger_function();
