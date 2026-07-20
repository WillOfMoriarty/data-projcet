-- =================================
--     REVENUE & LEAKAGE QUERIES
-- =================================

-- Total Revenue (Uang masuk dari pembayaran yang sukses/Paid)
SELECT
    SUM(amount) AS total_revenue
FROM payments
WHERE payment_status = 'Paid';

-- Revenue Berdasarkan Plan (Melihat kontribusi pendapatan tiap paket)
SELECT
    s.plan,
    SUM(p.amount) AS revenue
FROM payments p
JOIN subscriptions s ON p.customer_id = s.customer_id
WHERE p.payment_status = 'Paid'
GROUP BY s.plan
ORDER BY revenue DESC;

-- Total Revenue Loss (Total uang yang hilang dari pelanggan Churn)
SELECT
    SUM(p.amount) AS lost_revenue
FROM payments p
JOIN subscriptions s ON p.customer_id = s.customer_id
WHERE
    p.payment_status = 'Paid'
    AND s.status = 'Churned';

-- Revenue Loss Berdasarkan Plan (Mencari paket kebocoran terbesar)
-- Catatan: Paket 'Basic' biasanya jadi kontributor utama di segmen ini
SELECT
    s.plan,
    SUM(p.amount) AS lost_revenue
FROM payments p
JOIN subscriptions s ON p.customer_id = s.customer_id
WHERE
    p.payment_status = 'Paid'
    AND s.status = 'Churned'
GROUP BY s.plan
ORDER BY lost_revenue DESC;

-- ===================================
-- TREND ANALYSIS (MRR & CHURN TREND)
-- ===================================
-- Monthly Revenue (MRR Trend bulanan perusahaan)
SELECT
    DATE_TRUNC('month', payment_date) AS month,
    SUM(amount) AS revenue
FROM payments
WHERE payment_status = 'Paid'
GROUP BY month
ORDER BY month;

-- Monthly Churn Trend (Melihat tren waktu pelanggan berhenti langganan)
SELECT
    DATE_TRUNC('month', end_date) AS month,
    COUNT(*) AS churned_customer
FROM subscriptions
WHERE status = 'Churned'
GROUP BY month
ORDER BY month;