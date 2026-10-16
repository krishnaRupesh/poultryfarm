CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT REFERENCES products(product_id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    price NUMERIC(10, 2) NOT NULL,
    quantity INT NOT NULL,
    discount_price NUMERIC(10, 2),
    remarks TEXT,
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    customer_name VARCHAR(255) GENERATED ALWAYS AS (SELECT customer_name FROM customers WHERE customer_id = orders.customer_id),
    product_name VARCHAR(255) GENERATED ALWAYS AS (SELECT product_name FROM products WHERE product_id = orders.product_id)
);

CREATE TABLE orders_audit (
    audit_id SERIAL PRIMARY KEY,
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
    action VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION orders_audit_trigger_function() 
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO orders_audit (order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action)
        VALUES (NEW.order_id, NEW.customer_id, NEW.product_id, NEW.date, NEW.price, NEW.quantity, NEW.discount_price, NEW.remarks, NEW.total_amount, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, NEW.product_name, 'INSERT');
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO orders_audit (order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action)
        VALUES (NEW.order_id, NEW.customer_id, NEW.product_id, NEW.date, NEW.price, NEW.quantity, NEW.discount_price, NEW.remarks, NEW.total_amount, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, NEW.is_deleted, NEW.customer_name, NEW.product_name, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO orders_audit (order_id, customer_id, product_id, date, price, quantity, discount_price, remarks, total_amount, created_at, updated_at, created_by, updated_by, is_deleted, customer_name, product_name, action)
        VALUES (OLD.order_id, OLD.customer_id, OLD.product_id, OLD.date, OLD.price, OLD.quantity, OLD.discount_price, OLD.remarks, OLD.total_amount, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, OLD.is_deleted, OLD.customer_name, OLD.product_name, 'DELETE');
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION orders_audit_trigger_function();
