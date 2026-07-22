import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. Konfigurasi Antarmuka Web Dashboard
st.set_page_config(page_title="Fintech Fraud Detection Dashboard", layout="centered", page_icon="🛡️")
st.title("🛡️ Fraud Detection Predictive Dashboard")
st.write("Sistem Screening Awal Risiko Transaksi Finansial Berbasis Real-Time AI.")
st.markdown("---")

# 2. Memuat File Model & Artefak dari folder yang sama
try:
    saved_artifacts = joblib.load('fraud_detection_final_model.joblib')
    model = saved_artifacts['model']
    preprocessor = saved_artifacts['preprocessor'] # Load ColumnTransformer asli
    optimal_threshold = saved_artifacts['optimal_threshold']
except Exception as e:
    st.error(f"Gagal memuat file model. Pastikan file 'fraud_detection_final_model.joblib' berada di dalam folder 'app/'. Error: {e}")
    st.stop()

# 3. Desain Menu Input di Sisi Sidebar untuk Tim Operasional
st.sidebar.header("Input Parameter Transaksi Baru")
amount_input = st.sidebar.number_input("Nominal Transaksi (Amount)", min_value=0.0, value=150.0, step=10.0)
hour_input = st.sidebar.slider("Jam Kejadian Transaksi (Hour)", min_value=0, max_value=23, value=14)

# 4. Trigger Tombol Prediksi AI
if st.sidebar.button("Analisis Risiko Transaksi"):
    # Hitung fitur tambahan non-PCA sesuai bab preprocessing kita
    log_amount = np.log1p(amount_input)
    night_tx = 1 if 0 <= hour_input <= 5 else 0
    
    # Otomatisasi pengisian 28 fitur PCA (V1-V28) dengan nilai rata-rata dasar (0.0)
    pca_features = {f'V{i}': 0.0 for i in range(1, 29)}
    
    # Susun DataFrame mentah tepat mengikuti urutan kolom X_train SEBELUM di-scale
    # Urutan kolom wajib sama persis: Amount, Hour, V1-V28, Log_Amount, Night_Transaction
    raw_input_dict = {
        'Amount': amount_input,
        'Hour': hour_input,
        **pca_features,
        'Log_Amount': log_amount,
        'Night_Transaction': night_tx
    }
    raw_input_df = pd.DataFrame([raw_input_dict])
    
    # Transformasikan data mentah lewat pipeline preprocessor bawaan notebook lo (Otomatis RobustScale)
    scaled_input_array = preprocessor.transform(raw_input_df)
    
    # Kembalikan ke DataFrame karena Random Forest kita dilatih menggunakan format DataFrame
    # Catatan: ColumnTransformer memindahkan kolom 'Amount' & 'Hour' ke urutan paling depan
    scaled_cols = ['Amount', 'Hour'] + [col for col in raw_input_df.columns if col not in ['Amount', 'Hour']]
    final_input_df = pd.DataFrame(scaled_input_array, columns=scaled_cols)
    
    # Ekstrak skor probabilitas fraud dari model Random Forest (RUS)
    fraud_probability = model.predict_proba(final_input_df)[0, 1]
    
    # 5. Tampilkan Penilaian Skor & Risk Level Berdasarkan Threshold Kustom 0.8
    st.subheader("Hasil Evaluasi Prediktif Model")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Skor Probabilitas Fraud", value=f"{fraud_probability * 100:.2f}%")
        
    with col2:
        if fraud_probability >= optimal_threshold:
            st.error("RISK LEVEL: HIGH RISK (FRAUD)")
        elif fraud_probability >= 0.4:
            st.warning("RISK LEVEL: MEDIUM RISK")
        else:
            st.success("RISK LEVEL: LOW RISK (SAFE)")
            
    # 6. Tampilkan Rekomendasi Tindakan Operasional Bisnis
    st.subheader("💡 Rekomendasi Tindakan Operasional Bisnis")
    if fraud_probability >= optimal_threshold:
        st.markdown(f"""
        * 🟥 **BLOKIR OTOMATIS SEMENTARA**: Skor probabilitas ({fraud_probability*100:.1f}%) telah melampaui batas aman threshold bisnis (**{optimal_threshold}**).
        * Sistem diinstruksikan memblokir otorisasi kartu kredit nasabah secara real-time.
        * Kirimkan kode verifikasi OTP darurat atau aktivasi keamanan biometrik wajah ke smartphone pengguna.
        * Masukkan ID Transaksi ini ke daftar prioritas teratas tim *Fraud Analyst* untuk penanganan investigasi manual.
        """)
    elif fraud_probability >= 0.4:
        st.markdown("""
        * 🟨 **EVALUASI DAN MONITOR**: Nilai berada di zona abu-abu. Jangan tolak transaksi secara sepihak.
        * Loloskan dana transaksi, namun aktifkan bendera pemantauan (*flagging*) ekstra pada aktivitas akun pengguna ini selama 24 jam ke depan.
        """)
    else:
        st.markdown("""
        * 🟩 **SETUJUI TRANSAKSI (APPROVE)**: Transaksi dikategorikan bersih dan aman karena karakteristik datanya menyerupai pola perilaku belanja manusia normal.
        * Loloskan otorisasi dana langsung ke *payment gateway API*.
        """)
