# Direktori Kredensial (Credentials Directory)

Folder ini digunakan khusus untuk menyimpan berkas otentikasi keamanan dari Google Cloud Platform (GCP) yang diperlukan oleh aplikasi untuk mengakses **Google Cloud Vision API**.

## ⚠️ Peringatan Keamanan (Security Notice)
Demi menjaga keamanan akun dan menghindari penyalahgunaan kuota atau biaya yang tidak diinginkan, **jangan pernah mengunggah berkas kunci akses privat (`.json`) ke repositori publik seperti GitHub**. 

Folder ini telah dikonfigurasi melalui `.gitignore` untuk hanya mengunggah file panduan `README.md` ini ke repositori. Berkas JSON asli Anda akan tetap aman di komputer lokal Anda.

## Berkas yang Diperlukan
Aplikasi ini dirancang untuk membaca berkas kredensial dengan spesifikasi berikut:
* **Nama Berkas**: `google_credentials.json`
* **Format Berkas**: JSON (*Service Account Key*)
* **Lokasi**: `credentials/google_credentials.json`

## Langkah Mendapatkan Berkas Kredensial
Jika Anda baru saja melakukan kloning (*clone*) pada proyek ini, ikuti langkah berikut untuk mengaktifkan fitur OCR:
1. Buka [Google Cloud Console](https://google.com).
2. Buat proyek baru atau pilih proyek yang sudah ada.
3. Aktifkan **Cloud Vision API** pada proyek tersebut.
4. Buka menu **IAM & Admin** > **Service Accounts**.
5. Klik **Create Service Account**, isi detail yang diperlukan, lalu klik *Done*.
6. Klik pada akun layanan yang baru dibuat, masuk ke tab **Keys**.
7. Klik **Add Key** > **Create New Key**, pilih format **JSON**, lalu klik *Create*.
8. Berkas `.json` akan otomatis terunduh ke komputer Anda.
9. Pindahkan berkas tersebut ke dalam folder `credentials/` ini dan ubah namanya menjadi `google_credentials.json`.

---
*Catatan: Pastikan akun Google Cloud Anda telah mengaktifkan tautan pembayaran (Billing Account) agar proses permintaan API dari aplikasi tidak ditolak (Error 403).*
