-- Cek Total Baris Tiap Tabel
SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM subscriptions
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
UNION ALL
SELECT 'product_usage', COUNT(*) FROM product_usage
UNION ALL
SELECT 'support_tickets', COUNT(*) FROM support_tickets;

-- Cek Validasi Nilai Kosong (Missing Value Check) pada Subscriptions
-- Expected: Harus menghasilkan angka 14953 (sesuai summary quality)
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN end_date IS NULL THEN 1 ELSE 0 END) AS missing_end_date_count,
    ROUND(100.0 * SUM(CASE WHEN end_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_end_date_pct
FROM subscriptions;

-- Cek Jumlah Pelanggan Unik di Tabel Transaksi
-- Memastikan relasi ID antar tabel aman
SELECT
    (SELECT COUNT(DISTINCT customer_id) FROM customers) AS unique_customers_master,
    (SELECT COUNT(DISTINCT customer_id) FROM subscriptions) AS unique_customers_subs,
    (SELECT COUNT(DISTINCT customer_id) FROM payments) AS unique_customers_pay,
    (SELECT COUNT(DISTINCT customer_id) FROM product_usage) AS unique_customers_usage,
    (SELECT COUNT(DISTINCT customer_id) FROM support_tickets) AS unique_customers_tickets;