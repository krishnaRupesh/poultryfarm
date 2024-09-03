CREATE TABLE customer_balance_summary (
    customer_id INT PRIMARY KEY REFERENCES customers(customer_id),
    remaining_balance NUMERIC(10, 2) NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE customer_balance_summary_audit (
    audit_id SERIAL PRIMARY KEY,
    customer_id INT,
    remaining_balance NUMERIC(10, 2),
    last_updated TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION customer_balance_summary_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO customer_balance_summary_audit (customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.customer_id, NEW.remaining_balance, NEW.last_updated, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO customer_balance_summary_audit (customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.customer_id, NEW.remaining_balance, NEW.last_updated, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO customer_balance_summary_audit (customer_id, remaining_balance, last_updated, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (OLD.customer_id, OLD.remaining_balance, OLD.last_updated, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER customer_balance_summary_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON customer_balance_summary
FOR EACH ROW EXECUTE FUNCTION customer_balance_summary_audit_trigger_function();
