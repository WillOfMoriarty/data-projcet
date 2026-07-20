-- 1. Tabel Customers
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    signup_date TIMESTAMP NOT NULL,
    country VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    acquisition_channel VARCHAR(100),
    company_size VARCHAR(50),
    industry VARCHAR(100),
    last_login_date TIMESTAMP
);

-- 2. Tabel Subscriptions
CREATE TABLE subscriptions (
    subscription_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    plan VARCHAR(50),
    contract_type VARCHAR(50),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP, -- Diizinkan NULL karena 74% data kosong (masih aktif)
    status VARCHAR(50),
    monthly_fee INT,
    tenure_months INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 3. Tabel Payments
CREATE TABLE payments (
    payment_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    amount INT,
    payment_status VARCHAR(50),
    payment_method VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 4. Tabel Usage
CREATE TABLE product_usage (
    usage_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    usage_date TIMESTAMP NOT NULL,
    login_count INT,
    session_duration NUMERIC(10, 2), -- Menggunakan NUMERIC/DECIMAL untuk tipe float
    feature_used VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 5. Tabel Tickets
CREATE TABLE support_tickets (
    ticket_id INT PRIMARY KEY,
    customer_id INT, -- Diizinkan NULL jika ada ticket tanpa customer_id valid, sesuaikan kebutuhan
    created_date TIMESTAMP NOT NULL,
    issue_type VARCHAR(100),
    resolution_time_hours NUMERIC(10, 2),
    ticket_status VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
