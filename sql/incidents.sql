CREATE TABLE incidents (
    incident_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    incident_date DATE NOT NULL,
    summary TEXT,
    amount_spent NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE incidents_audit (
    audit_id SERIAL PRIMARY KEY,
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
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION incidents_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO incidents_audit (incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.incident_id, NEW.name, NEW.incident_type, NEW.incident_date, NEW.summary, NEW.amount_spent, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO incidents_audit (incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (NEW.incident_id, NEW.name, NEW.incident_type, NEW.incident_date, NEW.summary, NEW.amount_spent, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO incidents_audit (incident_id, name, incident_type, incident_date, summary, amount_spent, created_at, updated_at, created_by, updated_by, is_deleted, action)
        VALUES (OLD.incident_id, OLD.name, OLD.incident_type, OLD.incident_date, OLD.summary, OLD.amount_spent, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER incidents_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON incidents
FOR EACH ROW EXECUTE FUNCTION incidents_audit_trigger_function();
