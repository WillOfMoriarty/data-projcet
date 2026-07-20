# KPI Dictionary & Definition Document

**Project:** Customer Churn & Revenue Leakage Analytics  
**Phase:** KPI Development  
**Document Version:** 1.2 (Enterprise Portfolio Standard - Power BI Synced)  

---

## 1. KPI Governance Framework

Matriks tata kelola ini menetapkan akuntabilitas, frekuensi pembaruan data, dan batas toleransi performa untuk memastikan metrik bisnis dimonitor berdasarkan target operasional perusahaan.

| KPI Name | Department Owner | Refresh Frequency | Green Target | Yellow Warning | Red Critical |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Churn Rate | Customer Success | Daily | < 15.00% | 15.00% - 20.00% | > 20.00% |
| Revenue Loss Rate | Executive Team | Daily | < 5.00% | 5.00% - 10.00% | > 10.00% |
| ARPU | Finance | Weekly | > \$2,000 | \$1,500 - \$2,000 | < \$1,500 |
| Average Resolution Time | Customer Support | Daily | < 24.00 Hours | 24.00 - 36.00 Hours | > 36.00 Hours |
| Feature Adoption Rate | Product Management | Weekly | > 70.00% | 50.00% - 70.00% | < 50.00% |

---

## 2. Core KPI Dictionary

### 2.1 Customer & Retention Metrics

#### Total Customers
* **Definition:** Jumlah seluruh pelanggan unik yang tercatat di dalam database.
* **SQL Formula:** `SELECT COUNT(DISTINCT customer_id) FROM customers_clean`
* **DAX Formula:** `Total Customers = DISTINCTCOUNT(customers_clean[customer_id])`
* **Baseline Value:** 20,000 Customers
* **Business Purpose:** Mengukur skala volume absolut dari basis data pelanggan perusahaan.

#### Active Customers
* **Definition:** Jumlah pelanggan yang memiliki kontrak langganan aktif saat ini.
* **SQL Formula:** `SELECT COUNT(customer_id) FROM subscriptions_clean WHERE status = 'Active'`
* **DAX Formula:** `Active Customers = CALCULATE(DISTINCTCOUNT(customers_clean[customer_id]), subscriptions_clean[status] = "Active")`
* **Baseline Value:** 14,953 Customers
* **Business Purpose:** Mengetahui jumlah pengguna berjalan yang dilayani oleh operasional perusahaan.

#### Churned Customers
* **Definition:** Jumlah pelanggan yang telah memutuskan atau menghentikan kontrak langganannya.
* **SQL Formula:** `SELECT COUNT(customer_id) FROM subscriptions_clean WHERE status = 'Churned'`
* **DAX Formula:** `Churned Customers = CALCULATE(DISTINCTCOUNT(customers_clean[customer_id]), subscriptions_clean[status] = "Churned")`
* **Baseline Value:** 5,047 Customers
* **Business Purpose:** Menghitung volume kehilangan pelanggan sebagai bahan evaluasi strategi retensi.

#### Churn Rate
* **Definition:** Persentase pelanggan yang berhenti berlangganan dibandingkan dengan total basis pelanggan.
* **SQL Formula:** `(COUNT(customer_id) WHERE status = 'Churned' / COUNT(customer_id)) * 100`
* **DAX Formula:** `Churn Rate = DIVIDE([Churned Customers], [Total Customers], 0) * 100`
* **Baseline Value:** 25.24%
* **Business Purpose:** Metrik kesehatan bisnis utama untuk mengukur tingkat ketidakpuasan pelanggan atau kegagalan pasar.

#### Retention Rate
* **Definition:** Persentase pelanggan yang berhasil dipertahankan untuk tetap aktif berlangganan.
* **SQL Formula:** `(COUNT(customer_id) WHERE status = 'Active' / COUNT(customer_id)) * 100`
* **DAX Formula:** `Retention Rate = DIVIDE([Active Customers], [Total Customers], 0) * 100`
* **Baseline Value:** 74.76%
* **Business Purpose:** Mengukur tingkat stabilitas pendapatan berulang jangka panjang perusahaan.

#### Average Customer Lifetime
* **Definition:** Rata-rata durasi waktu dalam satuan bulan yang dihabiskan oleh pelanggan sebelum mereka resmi berhenti berlangganan atau hingga saat berjalan saat ini.
* **SQL Formula:** `AVG(tenure_months)`
* **DAX Formula:** `Average Customer Lifetime = AVERAGE(subscriptions_clean[tenure_months])`
* **Baseline Value:** Active: 15.98 Bulan | Churned: 9.99 Bulan
* **Business Purpose:** Menghitung durasi siklus hidup riil pelanggan untuk akurasi perhitungan Customer Lifetime Value (LTV).

---

### 2.2 Financial Metrics

#### Gross Realized Revenue (Total Pendapatan Sukses)
* **Definition:** Total akumulasi pendapatan kotor dari pembayaran seluruh transaksi pelanggan dengan status sukses.
* **SQL Formula:** `SELECT SUM(amount) FROM payments_clean WHERE payment_status = 'Paid'`
* **DAX Formula:** `Gross Revenue = CALCULATE(SUM(payments_clean[amount]), payments_clean[payment_status] = "Paid")`
* **Baseline Value:** \$41,389,440.00 (\$41.39M)
* **Business Purpose:** Melacak kinerja finansial kotor total (*top-line growth*) perusahaan historical.

#### Active Revenue (Revenue Berjalan)
* **Definition:** Akumulasi total pendapatan yang didapatkan dari pelanggan yang saat ini statusnya masih aktif berlangganan.
* **DAX Formula:** `Active Revenue = CALCULATE(SUM(payments_clean[amount]), payments_clean[payment_status] = "Paid", subscriptions_clean[status] = "Active")`
* **Baseline Value:** \$36,398,589.00
* **Business Purpose:** Memantau kontribusi dana masuk yang aman dan stabil dari pelanggan aktif saat ini.

#### Revenue Loss (Kebocoran Pendapatan)
* **Definition:** Total akumulasi pendapatan historis yang pernah dihasilkan oleh pelanggan sebelum mereka akhirnya memutuskan berhenti berlangganan.
* **SQL Formula:** `SUM(p.amount) FROM payments p JOIN subscriptions s ON p.customer_id = s.customer_id WHERE p.payment_status = 'Paid' AND s.status = 'Churned'`
* **DAX Formula:** `Revenue Loss = CALCULATE(SUM(payments_clean[amount]), payments_clean[payment_status] = "Paid", subscriptions_clean[status] = "Churned")`
* **Baseline Value:** \$4,990,851.00 (\$4.99M)
* **Business Purpose:** Menilai besaran kebocoran dana historis (*revenue leakage*) akibat kegagalan dalam menjaga retensi pengguna.

#### Revenue Loss Rate
* **Definition:** Rasio persentase kebocoran dana dari pelanggan *churn* terhadap total pendapatan kotor masuk.
* **SQL Formula:** `(Revenue Loss / Gross Realized Revenue) * 100`
* **DAX Formula:** `Revenue Loss Rate = DIVIDE([Revenue Loss], [Gross Revenue], 0) * 100`
* **Baseline Value:** 12.06%
* **Business Purpose:** Memantau tingkat kedaruratan finansial akibat *churn*. Rasio yang membesar menandakan inefisiensi biaya akuisisi.

#### ARPU (Average Revenue Per User)
* **Definition:** Rata-rata pendapatan akumulasi yang dihasilkan dari setiap basis pelanggan aktif berjalan.
* **SQL Formula:** `Active Revenue / (COUNT(customer_id) WHERE status = 'Active')`
* **DAX Formula:** `ARPU = DIVIDE([Active Revenue], [Active Customers], 0)`
* **Baseline Value:** \$2,434.20 per Customer Aktif
* **Business Purpose:** Menilai nilai ekonomis riil dari portofolio pengguna aktif saat ini tanpa bias dari pengguna yang sudah tidak menghasilkan pendapatan berjalan.

---

### 2.3 Product Engagement & Support Metrics

#### Average Tickets per Customer
* **Definition:** Rasio rata-rata jumlah tiket komplain yang diajukan oleh satu basis pelanggan.
* **SQL Formula:** `COUNT(ticket_id) / COUNT(DISTINCT customer_id)`
* **DAX Formula:** `Avg Tickets per Customer = DIVIDE(COUNT(support_tickets_clean[ticket_id]), DISTINCTCOUNT(customers_clean[customer_id]), 0)`
* **Baseline Value:** Active: 2.10 Tiket | Churned: 3.23 Tiket
* **Business Purpose:** Mengukur tingkat kerumitan sistem produk atau stabilitas performa aplikasi dari sudut pandang user.

#### Average Resolution Time
* **Definition:** Rata-rata waktu (dalam jam) yang dibutuhkan oleh tim dukungan teknis untuk menyelesaikan masalah hingga status tiket ditutup.
* **SQL Formula:** `AVG(resolution_time_hours)`
* **DAX Formula:** `Avg Resolution Time = AVERAGE(support_tickets_clean[resolution_time_hours])`
* **Baseline Value:** Active: 21.11 Jam | Churned: 22.69 Jam
* **Business Purpose:** Mengukur efisiensi kerja tim operasional Customer Support dalam menjaga kepuasan pengguna.

#### Feature Adoption Rate
* **Definition:** Rata-rata persentase jumlah fitur unik yang digunakan secara aktif oleh setiap pelanggan dari total 5 fitur utama platform.
* **DAX Formula:** 
    ```dax
    Feature Adoption Rate = 
    AVERAGEX(
        DISTINCT(product_usage_clean[customer_id]),
        DIVIDE(CALCULATE(DISTINCTCOUNT(product_usage_clean[feature_used])), 5, 0)
    )
    ```
* **Business Purpose:** Mengukur tingkat kebergunaan produk (*product-market fit*) agar tidak bias oleh kalkulasi tabel global.

---

## 3. Executive Dashboard Interface Layout

Berikut adalah rancangan visual penempatan kartu KPI utama di bagian atas halaman ringkasan eksekutif untuk kemudahan pemindaian informasi (*at-a-glance scanning*):

```text
+-----------------------+ +-----------------------+ +-----------------------+

| TOTAL CUSTOMERS       | | ACTIVE CUSTOMERS      | | CHURN RATE            |
| Current: 20,000       | | Current: 14,953       | | Current: 25.24%       |
| Status: Baseline      | | Status: Stable        | | Status: CRITICAL (RED)|
+-----------------------+ +-----------------------+ +-----------------------+

+-----------------------+ +-----------------------+ +-----------------------+

| GROSS REVENUE         | | REVENUE LOSS          | | RETENTION RATE        |
| Current: \$41.39M      | | Current: \$4.99M       | | Current: 74.76%       |
| Status: Target Met    | | Status: WARNING (YEL) | | Status: Stable        |
+-----------------------+ +-----------------------+ +-----------------------+
```

---

## 4. Analytical Segmentation Dimensions

Metrik utama di atas wajib dipecah (*drill-down*) berdasarkan dimensi analitik berikut pada visualisasi grafik detail:
1. **Revenue by Plan:** Paket `Basic`, `Standard`, `Premium`, atau `Enterprise` yang menjadi penopang utama profit.
2. **Churn by Plan:** Paket dengan tingkat kerapuhan sistem atau pembatalan kontrak tertinggi.
3. **Churn by Company Size:** Penilaian perilaku retensi berdasarkan ukuran skala bisnis pelanggan (`Small`, `Medium`, `Large`) untuk penyesuaian strategi tim Sales.
