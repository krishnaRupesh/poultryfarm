CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    payment_amount NUMERIC(10, 2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_mode VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE payments_audit (
    audit_id SERIAL PRIMARY KEY,
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
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION payments_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO payments_audit (payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.payment_id, NEW.customer_id, NEW.payment_amount, NEW.payment_date, NEW.payment_mode, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO payments_audit (payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.payment_id, NEW.customer_id, NEW.payment_amount, NEW.payment_date, NEW.payment_mode, NEW.remarks, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO payments_audit (payment_id, customer_id, payment_amount, payment_date, payment_mode, remarks, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (OLD.payment_id, OLD.customer_id, OLD.payment_amount, OLD.payment_date, OLD.payment_mode, OLD.remarks, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payments_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON payments
FOR EACH ROW EXECUTE FUNCTION payments_audit_trigger_function();
