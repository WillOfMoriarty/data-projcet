-- =========================================
--          BASIC BUSINESS QUERIES
-- =========================================

-- Total Customer (Menghitung seluruh basis pelanggan)
SELECT COUNT(*) AS total_customers
FROM customers;

-- Active vs Churned (Melihat Perbandingan jumlah status pelanggan)
SELECT
    status,
    COUNT(*) as total_customers
FROM subscriptions
GROUP BY status;

-- Churn Rate (Ekspektasi Output : 25.24%)
SELECT
    ROUND(
        100 * 
        SUM(
            CASE
                WHEN status = 'Churned' THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS churn_rate
FROM subscriptions;

-- =========================================
--       CUSTOMER SEGMENTATION QUERIES
-- =========================================

-- Churn Rate Berdasarkan Plan (Mencari paket dengan tingkat Churn tertinggi)
SELECT
    plan,
    COUNT(*) AS total_customers,
    SUM(
        CASE
            WHEN status = 'Churned' THEN 1
            ELSE 0
        END
    ) as churned_customers,
    ROUND(
        100.0 * 
        SUM(
            CASE
                WHEN status = 'Churned' THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS churn_rate
FROM subscriptions
GROUP BY plan
ORDER BY churn_rate DESC;

-- Churn Rate Berdasarkan Ukuran Perusahaan (Company Size)
SELECT
    c.company_size,
    COUNT(*) AS total_customer,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN s.status = 'Churned' THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS churn_rate
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.company_size
ORDER BY churn_rate DESC;

-- Churn Rate Berdasarkan Saluran Akuisisi (Acquisition Channel)
SELECT
    c.acquisition_channel,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN s.status = 'Churned' THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS churn_rate
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.acquisition_channel
ORDER BY churn_rate DESC;