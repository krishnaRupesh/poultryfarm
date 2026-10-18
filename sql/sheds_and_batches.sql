-- ===========================================================================
-- Sheds & Flock Batches DDL, Triggers, and Migration for SQLite & PostgreSQL
-- ===========================================================================

-- 1. SHEDS TABLE & AUDIT
CREATE TABLE IF NOT EXISTS sheds (
    shed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shed_name VARCHAR(100) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL DEFAULT 10000,
    shed_type VARCHAR(50) DEFAULT 'Layer',
    status VARCHAR(50) DEFAULT 'Active',
    location VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sheds_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shed_id INT,
    shed_name VARCHAR(100),
    capacity INT,
    shed_type VARCHAR(50),
    status VARCHAR(50),
    location VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(255),
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_sheds_insert
AFTER INSERT ON sheds
BEGIN
    INSERT INTO sheds_audit (
        shed_id, shed_name, capacity, shed_type, status, location, description,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        NEW.shed_id, NEW.shed_name, NEW.capacity, NEW.shed_type, NEW.status, NEW.location, NEW.description,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.deleted_at, NEW.deleted_by, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_sheds_update
AFTER UPDATE ON sheds
BEGIN
    INSERT INTO sheds_audit (
        shed_id, shed_name, capacity, shed_type, status, location, description,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        NEW.shed_id, NEW.shed_name, NEW.capacity, NEW.shed_type, NEW.status, NEW.location, NEW.description,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.deleted_at, NEW.deleted_by, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_sheds_delete
AFTER DELETE ON sheds
BEGIN
    INSERT INTO sheds_audit (
        shed_id, shed_name, capacity, shed_type, status, location, description,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        OLD.shed_id, OLD.shed_name, OLD.capacity, OLD.shed_type, OLD.status, OLD.location, OLD.description,
        OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.deleted_at, OLD.deleted_by, 'DELETE'
    );
END;

-- 2. FLOCK BATCHES TABLE & AUDIT
CREATE TABLE IF NOT EXISTS flock_batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_name VARCHAR(100) NOT NULL UNIQUE,
    shed_id INTEGER REFERENCES sheds(shed_id),
    breed VARCHAR(100) DEFAULT 'Layer (BV300)',
    bird_type VARCHAR(50) DEFAULT 'Layer',
    placement_date DATE NOT NULL,
    initial_birds INTEGER NOT NULL,
    current_birds INTEGER NOT NULL,
    initial_age_weeks INTEGER DEFAULT 18,
    status VARCHAR(50) DEFAULT 'Active',
    depletion_date DATE,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS flock_batches_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INT,
    batch_name VARCHAR(100),
    shed_id INT,
    breed VARCHAR(100),
    bird_type VARCHAR(50),
    placement_date DATE,
    initial_birds INT,
    current_birds INT,
    initial_age_weeks INT,
    status VARCHAR(50),
    depletion_date DATE,
    remarks TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    is_deleted BOOLEAN,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(255),
    action VARCHAR(10) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_flock_batches_insert
AFTER INSERT ON flock_batches
BEGIN
    INSERT INTO flock_batches_audit (
        batch_id, batch_name, shed_id, breed, bird_type, placement_date,
        initial_birds, current_birds, initial_age_weeks, status, depletion_date, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        NEW.batch_id, NEW.batch_name, NEW.shed_id, NEW.breed, NEW.bird_type, NEW.placement_date,
        NEW.initial_birds, NEW.current_birds, NEW.initial_age_weeks, NEW.status, NEW.depletion_date, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.deleted_at, NEW.deleted_by, 'INSERT'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_flock_batches_update
AFTER UPDATE ON flock_batches
BEGIN
    INSERT INTO flock_batches_audit (
        batch_id, batch_name, shed_id, breed, bird_type, placement_date,
        initial_birds, current_birds, initial_age_weeks, status, depletion_date, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        NEW.batch_id, NEW.batch_name, NEW.shed_id, NEW.breed, NEW.bird_type, NEW.placement_date,
        NEW.initial_birds, NEW.current_birds, NEW.initial_age_weeks, NEW.status, NEW.depletion_date, NEW.remarks,
        NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.deleted_at, NEW.deleted_by, 'UPDATE'
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_flock_batches_delete
AFTER DELETE ON flock_batches
BEGIN
    INSERT INTO flock_batches_audit (
        batch_id, batch_name, shed_id, breed, bird_type, placement_date,
        initial_birds, current_birds, initial_age_weeks, status, depletion_date, remarks,
        created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, deleted_by, action
    ) VALUES (
        OLD.batch_id, OLD.batch_name, OLD.shed_id, OLD.breed, OLD.bird_type, OLD.placement_date,
        OLD.initial_birds, OLD.current_birds, OLD.initial_age_weeks, OLD.status, OLD.depletion_date, OLD.remarks,
        OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.deleted_at, OLD.deleted_by, 'DELETE'
    );
END;
