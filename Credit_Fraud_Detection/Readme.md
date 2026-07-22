# Credit Card Fraud Detection with Cost-Sensitive AI

Proyek Machine Learning *end-to-end* ini membangun sistem *screening* awal otomatis untuk mendeteksi fraud kartu kredit secara *real-time*. Berbeda dengan proyek standar yang hanya fokus pada akurasi matematika kering, proyek ini dievaluasi berdasarkan **dampak finansial nyata (Cost-Sensitive Learning)** untuk meminimalkan kerugian operasional dan menyelamatkan aset perusahaan fintech.

---

### Proyek Goal & Dampak Bisnis
* **Problem**: Kelolosan transaksi fraud (*False Negative*) merugikan perusahaan Rp5.000.000/kasus, sedangkan salah memblokir transaksi nasabah normal (*False Positive*) memakan biaya investigasi operasional/CS sebesar Rp25.000/kasus.
* **Solusi AI**: Mengoptimalkan *trade-off* antara Precision dan Recall menggunakan algoritma Machine Learning yang dikombinasikan dengan strategi penyeimbangan data dan optimasi threshold kustom.
* **Hasil Akhir**: Model terbaik sukses menekan sisa total biaya kerugian finansial perusahaan ke titik terendah, yaitu **Rp 57.750.000** pada data pengujian.

---

### Alur Kerja & Metodologi
1. **Data Understanding**: Menangani dataset *Extremely Imbalanced* dari Kaggle (~285k transaksi, di mana kasus Fraud hanya sebesar **0.173%**).
2. **Feature Engineering**: Mengekstrak pola jam harian (`Hour`), penanda jam rawan tidur (`Night_Transaction`), dan transformasi penstabil distribusi (`Log_Amount`).
3. **Integrated Pipeline**: Penggabungan *RobustScaler* dan teknik sampling ke dalam satu jalur `ColumnTransformer` otomatis untuk mencegah kebocoran informasi (*data leakage*).
4. **Eksperimen Multi-Model**: Mengotomatisasi pelatihan 16 kombinasi eksperimen silang menggunakan *Logistic Regression, Decision Tree, Random Forest,* dan *LightGBM*.

---

### Hasil Optimasi Biaya Bisnis (Cost-Sensitive Evaluation)
Berdasarkan simulasi pergeseran batas probabilitas dari 0.1 s/d 0.9, ditemukan bukti empiris bahwa threshold default 0.5 bukanlah batas terbaik untuk bisnis finansial.

* **Strategi Pemenang**: **Random Forest + RUS (Random Under Sampling)**
* **Threshold Optimal**: **0.8** (Menaikkan threshold berhasil meredam salah blokir tanpa meloloskan banyak fraud).
* **Kasus Lolos (FN)**: 11 Transaksi
* **Kasus Salah Blokir (FP)**: 110 Transaksi
* **Dampak Keuangan**: Titik minimum kurva biaya tercapai secara mutlak pada Threshold 0.8, berhasil menghemat dana hingga ratusan juta rupiah jika dibandingkan dengan model baseline biasa.

---

### ⚠️ Project Limitations
* **Keterbatasan Semantik Fitur**: Dataset menggunakan komponen laten hasil **Principal Component Analysis (V1–V28)** demi privasi nasabah. Akibatnya, model tidak dapat diinterpretasikan secara semantik bisnis langsung (seperti mendeteksi lokasi atau jenis merchant).
* **Kesiapan Produksi (Blind Spot AI)**: Model ini belum bisa langsung dilepas 100% di sistem produksi nyata karena algoritma berbasis pohon (*tree*) tidak mampu melakukan ekstrapolasi terhadap anomali nilai ekstrem baru yang belum pernah dilihat (misal: input nominal transaksi Rp8 kuadriliun).
* **Arsitektur Dunia Nyata**: Implementasi fintech yang ideal membutuhkan data transaksi asli tanpa PCA, rekayasa fitur yang lebih kaya (perubahan perangkat, geo-location), serta wajib dikombinasikan dengan *Rule Engine (Hard Rules)* sebagai garda depan pertahanan sebelum dilempar ke model AI.

---

### 🏆 Key Takeaways (Kompetensi yang Dikuasai)
Melalui pengerjaan proyek ini, saya berhasil menguasai beberapa kompetensi data science tingkat *advanced*:
1. **Handling Extreme Imbalanced Data**: Mahir menyeimbangkan data timpang menggunakan metode sampling *Random Under Sampling (RUS)* dan *Robust Feature Scaling*.
2. **Integrated Data Pipeline Architecture**: Memahami cara membungkus alur preprocessing menggunakan objek Scikit-Learn untuk menjamin validitas data uji.
3. **Cost-Sensitive Evaluation Philosophy**: Menggeser pola pikir dari metrik matematika biasa (Akurasi/ROC-AUC) ke arah metrik finansial nyata (*Business Cost*) yang dipahami oleh tim manajemen bisnis.
4. **Non-Linear Decision Threshold Optimization**: Mampu melakukan simulasi pergeseran ambang batas keputusan (*threshold custom*) untuk mencari titik temu biaya operasional paling hemat.
5. **Hybrid Security Dashboard Deployment**: Berhasil mendeploy model ke aplikasi web interaktif menggunakan *Streamlit*, sekaligus mengimplementasikan arsitektur keamanan *hybrid* (ML Model + Hard Heuristic Rule) seperti yang diterapkan pada industri fintech global nyata (Stripe, Stripe, Midtrans).

---

### Tech Stack & Struktur Folder
* **Tools**: Python, Pandas, Numpy, Scikit-Learn, Imbalanced-Learn, LightGBM, Matplotlib, Seaborn, Streamlit, Joblib.

**Struktur Repositori:**
```text
├── data/           # Tempat dataset mentah (creditcard.csv)
├── notebook/       # Jupyter Notebook (Eksperimen, Kurva EDA, & Visualisasi Biaya)
└── app/            # Kode Web Application (app.py & model.joblib)
```

---

### Cara Menjalankan Aplikasi Web (Streamlit)
Aplikasi web ini dilengkapi dengan *Hybrid System* (ML + Hard Rule batas atas harian) untuk simulasi keamanan fintech dunia nyata.

1. Masuk ke folder aplikasi lewat terminal:
   ```bash
   cd app
   ```
2. Jalankan server Streamlit:
   ```bash
   streamlit run app.py
   ```
