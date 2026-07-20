-- ==========================================
--      CUSTOMER ENGAGEMENT QUERIES
-- ==========================================

-- Rata-rata Login berdasarkan Status (Aktif vs Churn)
SELECT
    s.status,
    AVG(u.login_count) AS avg_login
FROM product_usage u
JOIN subscriptions s ON u.customer_id = s.customer_id
GROUP BY s.status;

-- Rata-rata Jumlah Tiket Komplain per Pelanggan berdasarkan Status
SELECT
    s.status,
    COUNT(t.ticket_id) * 1.0 / COUNT(DISTINCT t.customer_id) AS avg_ticket
FROM support_tickets t
JOIN subscriptions s ON t.customer_id = s.customer_id
GROUP BY s.status;


-- ====================================================================
--              TOP RISK SEGMENT (PORTFOLIO HERO QUERY)
-- Mencari kombinasi Ukuran Perusahaan & Plan dengan Churn Rate tertinggi
-- ====================================================================

-- Analisis Segmen Risiko Tinggi
SELECT
    c.company_size,
    s.plan,
    COUNT(*) AS total_customers,
    ROUND(
        100.0 * SUM(CASE WHEN s.status = 'Churned' THEN 1 ELSE 0 END) 
        / COUNT(*)::NUMERIC, 
        2
    ) AS churn_rate
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.company_size, s.plan
ORDER BY churn_rate DESC;


-- ====================================================================
--              BUILD ANALYTICS VIEW (BACKEND DATASET)
-- Membuat View permanen yang siap ditarik ke Tableau / Power BI
-- ====================================================================

-- Drop View jika sebelumnya sudah pernah dibuat (mencegah error)
DROP VIEW IF EXISTS customer_analytics;

-- Create Master Analytical View
CREATE VIEW customer_analytics AS
SELECT
    c.customer_id,
    c.country,
    c.company_size,
    c.industry,
    s.plan,
    s.status,
    s.monthly_fee,
    s.tenure_months,
    COUNT(DISTINCT t.ticket_id) AS ticket_count,
    SUM(
        CASE
            WHEN p.payment_status = 'Paid' THEN p.amount
            ELSE 0
        END
    ) AS total_revenue
FROM customers c
LEFT JOIN subscriptions s ON c.customer_id = s.customer_id
LEFT JOIN payments p ON c.customer_id = p.customer_id
LEFT JOIN support_tickets t ON c.customer_id = t.customer_id
GROUP BY
    c.customer_id,
    c.country,
    c.company_size,
    c.industry,
    s.plan,
    s.status,
    s.monthly_fee,
    s.tenure_months;

-- Tes panggil isi VIEW (Memastikan View bekerja dengan lancar)
SELECT * FROM customer_analytics LIMIT 10;
