CREATE TABLE subscriptions (
    subscription_id INT PRIMARY KEY,
    user_id INT,
    plan VARCHAR(20),
    monthly_revenue DECIMAL(10,2),
    status VARCHAR(20),
    start_date DATE,
    churn_date DATE,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);