# Receipt OCR & Automated Parser Pipeline 

Proyek ini adalah sebuah aplikasi berbasis web modular yang dirancang untuk melakukan pemindaian, ekstraksi, dan pemrosesan teks dari gambar struk belanja menggunakan Google Cloud Vision API dan Streamlit.

---

### 💡 Latar Belakang & Tujuan Proyek
Proyek ini dibangun secara mandiri sebagai bentuk eksperimen teknologi dan pemanfaatan perangkat kecerdasan buatan (*AI-assisted development*) untuk mempercepat proses penulisan sintaksis serta konfigurasi komponen. 

Tujuan utama dari proyek ini adalah sebagai sarana pembelajaran praktis (*hands-on learning*) dalam memahami eksplorasi teknologi berikut:
1. **Image Preprocessing**: Memanfaatkan OpenCV untuk meningkatkan kualitas keterbacaan gambar struk sebelum diproses oleh mesin OCR.
2. **Cloud API Integration**: Mengintegrasikan SDK Google Cloud Vision secara aman menggunakan mekanisme otentikasi akun layanan (*Service Account*).
3. **Structured Data Storage**: Menyimpan dan mengelola hasil parsing teks terstruktur ke dalam database relasional lokal (SQLite).
4. **Rapid UI Prototyping**: Membangun antarmuka pengguna yang responsif dan interaktif menggunakan framework Streamlit.

---

### 🛠️ Spesifikasi Teknologi (Tech Stack)
* **Bahasa Pemrograman**: Python 3.x
* **Antarmuka Pengguna**: Streamlit
* **Pengolahan Citra**: OpenCV (`cv2`), NumPy, & Pillow (PIL)
* **Mesin OCR**: Google Cloud Vision SDK (`DOCUMENT_TEXT_DETECTION`)
* **Penyimpanan Data**: SQLite3 (Standard Library)

---

### 📁 Struktur Proyek
Aplikasi ini menggunakan arsitektur folder modular untuk memisahkan logika bisnis, antarmuka pengguna, dan manajemen aset:
* `app/`: Berisi seluruh kode sumber utama aplikasi (`main.py`, `preprocess.py`, `ocr.py`, dll).
* `credentials/`: Tempat penyimpanan file otentikasi Google Cloud (diabaikan oleh Git demi keamanan).
* `data/`: Folder penyimpanan untuk basis data SQLite dan log hasil OCR.
* `notebooks/`: Berisi berkas eksperimen tahap awal (*Jupyter Notebook*).

---

### 🚀 Panduan Instalasi dan Penggunaan

Jika Anda ingin mereplikasi atau mencoba proyek ini di lingkungan lokal Anda, silakan ikuti langkah-langkah berikut:

#### 1. Kloning Repositori
```bash
git clone <url-repositori-anda>
cd Receipt-OCR
```

#### 2. Instalasi Dependensi
Pastikan pustaka (*libraries*) yang diperlukan telah terinstal dengan menjalankan perintah:
```bash
pip install streamlit google-cloud-vision opencv-python pillow numpy
```

#### 3. Konfigurasi Kredensial Google Cloud
Demi keamanan data, kunci akses API tidak disertakan dalam repositori ini. Anda perlu menyiapkannya secara mandiri:
1. Aktifkan **Cloud Vision API** pada Google Cloud Console Anda.
2. Buat sebuah *Service Account* dan unduh kunci privat dalam format `.json`.
3. Buat folder baru bernama `credentials/` di direktori utama proyek ini.
4. Simpan file tersebut di dalam folder tersebut dengan nama `google_credentials.json`.
   *(Catatan: Pastikan Billing Account pada Google Cloud Anda telah aktif untuk menghindari error 403 / Permission Denied).*

#### 4. Menjalankan Aplikasi
Eksekusi perintah berikut melalui terminal untuk memulai server lokal Streamlit:
```bash
streamlit run app/main.py
```

---
*Proyek ini dikembangkan secara efisien menggunakan metodologi AI-assisted programming untuk mengoptimalkan alur kerja pengkodean tanpa mengurangi validitas logika sistem.*
