# Laporan Kualitas Data

## Ringkasan Eksekutif

Penilaian kualitas data formal telah dilakukan di lima dimensi: Kelengkapan (*Completeness*), Keunikan (*Uniqueness*), Validitas (*Validity*), Konsistensi (*Consistency*), dan Integritas Referensial (*Referential Integrity*).

Dataset ini lolos semua pemeriksaan kualitas utama dan dinyatakan layak digunakan untuk keperluan analisis maupun pelaporan bisnis.

---

## Kelengkapan (*Completeness*)

Nilai yang hilang (*missing values*) ditemukan pada kolom-kolom berikut:

* end_date
* last_login_date

Nilai yang hilang ini dinilai valid dan memang sewajarnya terjadi berdasarkan proses bisnis:

* `end_date` bernilai kosong (null) untuk pelanggan dengan status langganan aktif.
* `last_login_date` bernilai kosong (null) untuk pelanggan yang belum pernah masuk (*login*) ke platform.

Tidak ditemukan masalah kelengkapan data yang bersifat kritis.

---

## Keunikan (*Uniqueness*)

Validasi kunci utama (*primary key*) telah dilakukan pada:

* customer_id
* subscription_id
* payment_id
* usage_id
* ticket_id

Tidak ditemukan adanya duplikasi pada kunci utama (*primary key*).

---

## Validitas (*Validity*)

Aturan validasi bisnis telah diterapkan pada:

* Usia pelanggan (*Customer age*)
* Durasi sesi (*Session duration*)
* Jumlah pembayaran (*Payment amount*)
* Masa langganan (*Subscription tenure*)
* Status langganan (*Subscription status*)

Tidak ditemukan adanya rekor data yang tidak valid.

---

## Konsistensi (*Consistency*)

Pemeriksaan konsistensi silang antar-tabel (*cross-table*) telah dilakukan:

* Tanggal mulai langganan <= tanggal berakhir (`Subscription start date <= end date`)
* Tanggal pembayaran >= tanggal mulai langganan (`Payment date >= subscription start date`)
* Tanggal penggunaan >= tanggal pendaftaran (`Usage date >= signup date`)
* Tanggal tiket kendala >= tanggal pendaftaran (`Ticket date >= signup date`)

Semua hubungan/relasi tanggal dinyatakan valid.

---

## Integritas Referensial (*Referential Integrity*)

Hubungan kunci asing (*foreign key*) telah divalidasi antara data pelanggan dengan semua tabel transaksi.

Tidak ditemukan adanya data yatim (*orphan records* / data transaksi tanpa identitas pelanggan yang jelas).

---

## Skor Kualitas Data

| Dimensi | Skor |
| :--- | :--- |
| Kelengkapan (*Completeness*) | 99.5% |
| Keunikan (*Uniqueness*) | 100% |
| Validitas (*Validity*) | 100% |
| Konsistensi (*Consistency*) | 100% |
| Integritas Referensial (*Referential Integrity*) | 100% |

---

## Penilaian Keseluruhan

Dataset ini dinyatakan **siap untuk dianalisis** (*analysis-ready*) dan telah memenuhi standar kualitas yang dibutuhkan untuk analisis eksploratif (EDA), pembuatan KPI, analitik pelanggan, analisis *churn*, serta pembuatan pelaporan *dashboard*.
