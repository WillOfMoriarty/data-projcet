# Dokumentasi Desain Data Sintetis

## Ringkasan (Overview)

Proyek ini menggunakan dataset pelanggan SaaS sintetis yang dirancang khusus untuk mensimulasikan lingkungan analisis churn pelanggan secara realistis.

Dataset ini tidak dibuat secara acak, melainkan sengaja ditanamkan pola bisnis tertentu. Pendekatan ini memastikan adanya hubungan yang bermakna antar-data. Dengan begitu, tahap Analisis Data Eksploratif (EDA), Analisis SQL, Pengembangan KPI, Pembuatan Dashboard, hingga Pemberian Rekomendasi Bisnis dapat menghasilkan wawasan yang logis dan aplikatif.

Tujuan bisnis utama dari proyek ini adalah untuk memahami perilaku churn pelanggan, menghitung kerugian pendapatan (revenue), mengidentifikasi pelanggan berisiko tinggi, dan memberikan rekomendasi berbasis data untuk meningkatkan retensi.

---

# Struktur Dataset

Proyek ini terdiri dari lima tabel yang saling berhubungan:

## 1. Customers (Pelanggan)

Berisi informasi demografis pelanggan, saluran akuisisi, dan ringkasan riwayat interaksi terakhir mereka.

| Kolom               | Deskripsi                                             |
| ------------------- | ----------------------------------------------------- |
| customer_id         | ID unik pelanggan                                     |
| signup_date         | Tanggal pendaftaran pelanggan                         |
| country             | Negara asal pelanggan                                 |
| age                 | Usia pelanggan                                        |
| gender              | Jenis kelamin pelanggan                               |
| acquisition_channel | Sumber saluran pemasaran (marketing)                  |
| company_size        | Ukuran perusahaan (Small, Medium, Large)              |
| industry            | Sektor industri pelanggan                             |
| last_login_date     | Tanggal terakhir pelanggan masuk ke sistem (Baru)     |

---

## 2. Subscriptions (Langganan)

Berisi detail paket berlangganan, tipe kontrak, dan status aktif/churn pelanggan.

| Kolom           | Deskripsi                                                        |
| --------------- | ---------------------------------------------------------------- |
| subscription_id | ID unik langganan                                                |
| customer_id     | ID unik pelanggan                                                |
| plan            | Paket langganan (Basic, Standard, Premium, Enterprise)           |
| contract_type   | Tipe kontrak berlangganan (Monthly, Annual) (Baru)               |
| start_date      | Tanggal mulai langganan                                          |
| end_date        | Tanggal berhenti langganan (hanya terisi jika status Churned)    |
| status          | Status siklus hidup pelanggan (Active atau Churned)              |
| monthly_fee     | Biaya langganan bulanan berdasarkan paket yang dipilih           |
| tenure_months   | Total durasi pelanggan telah berlangganan dalam satuan bulan (Baru)|

---

## 3. Payments (Pembayaran)

Berisi riwayat transaksi pembayaran bulanan pelanggan.

| Kolom         | Deskripsi                                          |
| ------------- | -------------------------------------------------- |
| payment_id     | ID unik transaksi pembayaran                       |
| customer_id    | ID unik pelanggan                                  |
| payment_date   | Tanggal transaksi pembayaran dilakukan             |
| amount         | Jumlah uang yang dibayarkan                        |
| payment_status | Status pembayaran (Paid, Failed, Refunded)        |
| payment_method | Metode pembayaran (Credit Card, PayPal, Bank Transfer) |

---

## 4. Product Usage (Penggunaan Produk)

Berisi metrik keaktifan dan interaksi pelanggan di dalam platform.

| Kolom           | Deskripsi                                    |
| --------------- | -------------------------------------------- |
| usage_id         | ID unik catatan penggunaan                   |
| customer_id      | ID unik pelanggan                            |
| usage_date       | Tanggal penggunaan                           |
| login_count      | Jumlah berapa kali pengguna masuk (login)    |
| session_duration | Durasi sesi penggunaan dalam satuan menit    |
| feature_used     | Fitur produk yang digunakan                  |

---

## 5. Support Tickets (Tiket Bantuan)

Berisi riwayat interaksi pelanggan dengan tim dukungan teknis.

| Kolom                | Deskripsi                               |
| --------------------- | --------------------------------------- |
| ticket_id             | ID unik tiket bantuan                   |
| customer_id           | ID unik pelanggan                       |
| created_date          | Tanggal pembuatan tiket                 |
| issue_type            | Jenis masalah (Bug, Billing, dll)       |
| resolution_time_hours | Durasi penyelesaian masalah dalam jam   |
| ticket_status         | Status akhir tiket (Resolved, Closed)   |

---

# Logika Churn Sintetis

Untuk menciptakan perilaku pelanggan yang realistis, peluang pelanggan untuk berhenti berlangganan (*churn probability*) dipengaruhi oleh keaktifan produk, kendala teknis, paket langganan, dan karakteristik perusahaan.

Peluang dasar churn (*baseline*) dimulai dari **5%**. Aturan berikut sengaja ditanamkan ke dalam logika pembuatan data:

---

## Aturan 1: Keaktifan Produk Rendah (Low Engagement)

### Asumsi
Pelanggan yang jarang masuk dan menggunakan produk memiliki kemungkinan jauh lebih besar untuk pergi.

### Logika Bisnis
Keaktifan yang rendah adalah salah satu indikator terkuat terjadinya churn pada bisnis SaaS berbasis langganan.

### Kondisi
Rata-rata jumlah login < 3

### Dampak Churn
Peluang churn naik sebesar **+60%**

---

## Aturan 2: Volume Tiket Bantuan Tinggi

### Asumsi
Pelanggan yang sering mengirimkan tiket bantuan biasanya sedang mengalami kendala atau tidak puas dengan produk.

### Logika Bisnis
Interaksi bantuan yang terlalu sering menandakan adanya masalah yang belum selesai, pengalaman pengguna yang buruk, atau ekspektasi yang tidak terpenuhi.

### Kondisi
Memiliki lebih dari 3 tiket bantuan

### Dampak Churn
Peluang churn naik sebesar **+50%**

---

## Aturan 3: Pelanggan Paket Basic

### Asumsi
Pelanggan dengan paket terendah umumnya memiliki komitmen yang rendah dan biaya migrasi (*switching cost*) yang kecil.

### Logika Bisnis
Pelanggan paket Basic lebih mudah pindah ke kompetitor karena ketergantungan produk yang minim dan tidak terikat kontrak besar.

### Kondisi
Paket Langganan = Basic

### Dampak Churn
Peluang churn naik sebesar **+35%**

---

## Aturan 4: Pelanggan Paket Enterprise

### Asumsi
Pelanggan tingkat Enterprise cenderung lebih stabil, setia, dan tidak mudah berganti vendor.

### Logika Bisnis
Pelanggan Enterprise biasanya melewati proses implementasi yang besar, memiliki manajer akun khusus, dan terikat kontrak jangka panjang.

### Kondisi
Paket Langganan = Enterprise

### Dampak Churn
Peluang churn turun sebesar **-8%** (mengurangi risiko)

---

## Aturan 5: Perusahaan Skala Kecil (Small)

### Asumsi
Perusahaan kecil umumnya sangat sensitif terhadap harga dan batasan anggaran operasional mereka.

### Logika Bisnis
Keterbatasan anggaran dan ketidakpastian bisnis pada skala kecil meningkatkan risiko pembatalan langganan.

### Kondisi
Ukuran Perusahaan = Small

### Dampak Churn
Peluang churn naik sebesar **+20%**

---

## Aturan 6: Komitmen Kontrak Tahunan (Annual) (Baru)

### Asumsi
Pelanggan yang memilih kontrak tahunan di awal jarang melakukan pembatalan di tengah jalan.

### Logika Bisnis
Komitmen kontrak yang lebih panjang memberikan stabilitas pendapatan bagi bisnis dan memperkecil celah waktu churn langsung.

### Kondisi
Tipe Kontrak = Annual

### Dampak Churn
Peluang churn turun sebesar **-10%** (mengurangi risiko)

---

# Ekspektasi Hasil Analisis

Semua aturan bisnis di atas dirancang agar kamu bisa menemukan pola-pola berikut saat melakukan analisis data nanti:

* Pelanggan dengan aktivitas login rendah akan menunjukkan angka churn yang tinggi.
* Pelanggan dengan banyak tiket komplain memiliki risiko churn yang melonjak tajam.
* Pelanggan Paket Basic akan lebih sering churn dibandingkan paket Premium atau Enterprise.
* Pelanggan Enterprise dan pengguna kontrak Tahunan (*Annual*) akan memiliki tingkat retensi paling kuat.
* Perusahaan kecil (*Small*) akan menyumbang angka churn lebih tinggi dibanding perusahaan Medium atau Large.
* Kerugian pendapatan (*Revenue Loss*) akan terlihat menumpuk pada segmen pelanggan yang berstatus Churned.

---

# Catatan Penting

Dataset ini sepenuhnya bersifat sintetis (tiruan) dan dibuat murni untuk keperluan edukasi serta portofolio data.

Pola bisnis yang dimasukkan didasarkan pada asumsi retensi umum industri SaaS. Tujuannya adalah menghasilkan dataset yang kaya akan cerita, sehingga mendukung proses analisis data, pembuatan dasbor visual, serta penyusunan rekomendasi bisnis yang berbobot.