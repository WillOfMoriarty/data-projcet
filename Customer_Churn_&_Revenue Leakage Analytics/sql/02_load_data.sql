-- 1. Load Data Customers Clean
COPY customers(customer_id, signup_date, country, age, gender, acquisition_channel, company_size, industry, last_login_date)
FROM 'C:/VSCode/customer-churn-analytics/data/processed/customers_clean.csv'
DELIMITER ','
CSV HEADER;

-- 2. Load Data Subscriptions Clean
COPY subscriptions(subscription_id, customer_id, plan, contract_type, start_date, end_date, status, monthly_fee, tenure_months)
FROM 'C:/VSCode/customer-churn-analytics/data/processed/subscriptions_clean.csv'
DELIMITER ','
CSV HEADER;

-- 3. Load Data Payments Clean
COPY payments(payment_id, customer_id, payment_date, amount, payment_status, payment_method)
FROM 'C:/VSCode/customer-churn-analytics/data/processed/payments_clean.csv'
DELIMITER ','
CSV HEADER;

-- 4. Load Data Product Usage Clean
COPY product_usage(usage_id, customer_id, usage_date, login_count, session_duration, feature_used)
FROM 'C:/VSCode/customer-churn-analytics/data/processed/product_usage_clean.csv'
DELIMITER ','
CSV HEADER;

-- 5. Load Data Support Tickets Clean
COPY support_tickets(ticket_id, customer_id, created_date, issue_type, resolution_time_hours, ticket_status)
FROM 'C:/VSCode/customer-churn-analytics/data/processed/support_tickets_clean.csv'
DELIMITER ','
CSV HEADER;
