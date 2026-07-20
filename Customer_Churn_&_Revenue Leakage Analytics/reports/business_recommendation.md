# Laporan Komprehensif: Analisis Churn, Kebocoran Pendapatan, & Strategi Intervensi Bisnis

## 1. Executive Summary & Macro Metrics Baseline
Analisis taktis ini didasarkan pada repositori data master dari **20.000 pelanggan unik B2B SaaS** perusahaan. Berdasarkan kalkulasi data historis, ditemukan metrik fundamental sebagai berikut:
*   **Total Master Customers**: 20.000 Akun Aktif Historis
    *   *Active Cohort*: 14.953 Akun (74,76%)
    *   *Churned Cohort*: 5.047 Akun (25,24%)
*   **Baseline Churn Rate**: 25,24% (Kalkulasi SQL: `100.0 * Churned / Total Customers`)
*   **Financial Impact**:
    *   *Total Realized Revenue (Active)*: $36.398,589,00
    *   *Total Revenue Loss (Churned)*: $4.990.851,00
    *   *Revenue Leakage Rate*: **12,06%** dari total potensi pendapatan hancur akibat churn.

Fakta krusial yang ditemukan dalam EDA ini adalah **Engagement Paradox**: metrik penggunaan platform seperti `avg_login` (~5.00) dan `avg_session` (~45 menit) terbukti **stagnan dan identik** di kedua cohort. Hal ini mematahkan asumsi bahwa pelanggan churn karena "lupa/tidak memakai produk". Pemicu utama mundurnya pelanggan murni disebabkan oleh akumulasi friksi pada *Customer Support Service* dan ketidaksesuaian *Pricing-to-Segment Model*.

---

## 2. Deep-Dive Temuan EDA & Matriks Rekomendasi Bisnis

### TEMUAN 1: Analisis Silang Risiko Paket 'Basic' & Kerugian Finansial Terbesar
*   **Hasil EDA Deep-Dive**: 
    *   Paket **Basic** mencatatkan angka churn yang sangat mengkhawatirkan sebesar **42,34%**. Sebagai perbandingan, tiga paket lainnya sangat stabil: Enterprise (11,32%), Premium (14,19%), dan Standard (14,14%).
    *   Secara nominal, paket Basic menyumbang kebocoran kas terbesar yaitu **$1.728.916,00**. Jika dikombinasikan dengan data *Company Size*, kerugian terbesar berpusat pada segmen **Small Business** yang mendominasi kehilangan uang sebesar **$3.759.275,00** (75,3% dari total kebocoran).
*   **Analisis Dampak Bisnis**: Terjadi kesalahan fatal pada penentuan ambang batas nilai (*value threshold*) paket murah. Pelanggan berskala kecil membanjiri paket Basic karena harganya, namun mereka langsung keluar (*churn*) secara massal karena fitur di paket tersebut tidak mampu menyelesaikan masalah operasional mereka, atau proses perpindahan ke paket Standard terlalu mahal.
*   **Rekomendasi Tindakan (Actionable Strategy)**:
    1.  **Gating & Value Restructuring**: Lakukan pembatasan (*gating*) ketat pada 2 dari 5 fitur inti platform di dalam paket Basic. Gunakan fitur tersebut sebagai *In-App Upgrade Hook*.
    2.  **Standard Tier Grace Period**: Implementasikan strategi *Tier Migration Campaign*. Untuk semua akun Small Business di paket Basic dengan masa aktif >6 bulan, tawarkan otomatisasi perpindahan ke paket Standard secara gratis selama 30 hari (*Free Trial Upgrade*) untuk membuktikan efisiensi kerja.
*   **Expected Outcome & KPI Target**:
    *   Menurunkan churn rate paket Basic dari 42,34% ke target **28%** dalam 2 kuartal.
    *   Mengonversi minimal 12% basis pengguna Basic menjadi pelanggan paket Standard, memulihkan *leaked revenue* sebesar **$200.000 - $350.000 ARR**.

---

### TEMUAN 2: Rasio Friksi Layanan (Support Friction Ratio) Sebagai Pemicu Churn
*   **Hasil EDA Deep-Dive**:
    *   Pelanggan aktif hanya membuat rata-rata **2,10 tiket** selama masa langganan mereka, sedangkan pelanggan yang churn melonjak hingga **3,23 tiket** (+53,8% lebih tinggi).
    *   Waktu penyelesaian masalah (*Average Resolution Time*) bagi pelanggan yang akhirnya churn juga jauh lebih lambat, yaitu mencapai **22,69 jam** dibanding grup aktif (21,11 jam).
    *   *Kalkulasi Rasio Friksi*: Setiap penambahan 1 tiket di atas ambang batas 2 tiket, dikombinasikan dengan waktu tunggu penyelesaian di atas 22 jam, meningkatkan probabilitas churn pelanggan hingga sebesar 35%.
*   **Analisis Dampak Bisnis**: Pengguna tidak meninggalkan platform karena tidak butuh fiturnya; mereka pergi karena merasa "ditinggalkan" saat menghadapi *bug* atau kendala transaksi. Kecepatan penanganan masalah oleh tim *support* berkorelasi langsung dengan keputusan pembatalan kontrak langganan.
*   **Rekomendasi Tindakan (Actionable Strategy)**:
    1.  **Power BI Real-Time Health-Trigger**: Manfaatkan perhitungan *Segment Churn Rate* dan *Segment Revenue Leakage* pada visualisasi *Tooltip*. Jika ada akun membuka tiket ke-3 dalam satu bulan, tandai akun tersebut dengan status **"High-Risk Support Friction"**.
    2.  **Dedicated Support Routing SLA**: Buat jalur *SLA (Service Level Agreement)* prioritas otomatis. Tiket dari akun berstatus risiko tinggi wajib diselesaikan dalam waktu kurang dari **12 jam** (memotong separuh dari waktu rata-rata churn saat ini yang sebesar 22,69 jam).
*   **Expected Outcome & KPI Target**:
    *   Membatasi akumulasi tiket per pengguna di angka maksimal **2,30 tiket**.
    *   Mempersingkat *resolution time* akun berisiko menjadi di bawah **14 jam**, yang diproyeksikan dapat menekan pembatalan sepihak sebesar **18%**.

---

### TEMUAN 3: Analisis Masa Bertahan (Tenure Critical Cliff) di Bulan Ke-10
*   **Hasil EDA Deep-Dive**:
    *   Terdapat kesenjangan waktu bertahan yang sangat drastis (*Tenure Gap*). Pelanggan yang aktif mampu bertahan hingga rata-rata **15,98 bulan**, sedangkan pelanggan yang churn ambruk dan keluar di rata-rata angka **9,99 bulan**.
    *   Ini mengidentifikasi adanya **"Retention Cliff" (Jurang Maut Retensi)** yang terjadi secara konsisten tepat pada rentang **bulan ke-9 hingga bulan ke-11**.
*   **Analisis Dampak Bisnis**: Bulan ke-10 adalah fase krusial di mana masa euforia penggunaan produk telah habis dan manajemen pelanggan mulai mengevaluasi pengeluaran anggaran mereka. Jika mereka tidak melihat bukti nyata keuntungan (*Return on Investment*) dari platform kita sebelum bulan ke-10, mereka dipastikan akan menolak memperpanjang kontrak.
*   **Rekomendasi Tindakan (Actionable Strategy)**:
    1.  **Month-8 Automated Value Realization Audit**: Pada bulan ke-8 (60 hari sebelum menyentuh jurang maut bulan ke-10), sistem wajib mengirimkan infografis dan laporan performa kustom ke email pembuat keputusan (*Decision Maker*) di perusahaan klien. Tunjukkan data konkret berupa durasi waktu yang berhasil mereka hemat dan intensitas penggunaan fitur mereka.
    2.  **Early Annual Renewal Incentives**: Pada bulan ke-9, tawarkan opsi penguncian harga (*Price-Lock*) atau bonus gratis 1 bulan jika mereka bersedia melakukan pembaruan kontrak jangka panjang (*Annual Contract*) lebih awal.
*   **Expected Outcome & KPI Target**:
    *   Menggeser rata-rata umur simpan cohort berisiko dari 9,99 bulan naik menjadi minimal **13,5 bulan**.
    *   Mengamankan perpanjangan kontrak lebih awal (*Early Renewal*) minimal sebesar 15% dari total akun yang memasuki masa kritis.

---

## 3. Matriks Prioritas Eksekusi Strategi (Impact vs Effort)

Untuk memudahkan tim manajemen dalam mengambil tindakan eksekusi dengan cepat, berikut adalah pemetaan prioritas kerja berdasarkan analisis data di atas:

| Prioritas | Langkah Tindakan | Sektor Target | Estimasi Tingkat Kesulitan (Effort) | Dampak Finansial (Impact) |
| :--- | :--- | :--- | :--- | :--- |
| **HIGH PRIORITY (Quick Wins)** | Otomatisasi Alarm Pelanggan Berisiko Tinggi di atas 2 Tiket (*SLA < 12 Jam*) | Customer Support / Operations | Rendah (Hanya setup rules di CRM/Power BI) | **Sangat Tinggi** (Langsung menahan kebocoran akun secara real-time) |
| **HIGH PRIORITY** | Audit Manfaat Manfaat Otomatis pada Bulan Ke-8 (*Month-8 ROI Report*) | Customer Success / Product | Sedang (Perlu integrasi data usage ke email template) | **Tinggi** (Mengamankan perpanjangan kontrak sebelum bulan ke-10) |
| **MEDIUM PRIORITY** | Pembatasan Fitur Paket Basic (*Gating Feature*) & Promosi Standard Tier | Product / Marketing | Tinggi (Perlu merubah struktur kode produk & pricing) | **Sangat Tinggi** (Menambal kebocoran terbesar senilai $1,72M) |
| **LOW PRIORITY** | Penyusunan Panduan Interaktif Onboarding Mandiri (*Self-Service Walkthrough*) | Product Team / UX | Sedang (Membuat alur guide baru di aplikasi) | **Sedang** (Membantu retensi awal untuk segmen Small Business) |
