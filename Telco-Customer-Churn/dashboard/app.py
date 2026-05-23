import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Main page configuration
st.set_page_config(
    page_title='Telco Customer Churn Dashboard',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.title("Customer Churn Analytics Dashboard")

@st.cache_data
def load_data():
    file_path = os.path.join('..', 'data', 'clean', 'Telco_Cus_Churn_Clean.csv')
    df = pd.read_csv(file_path)

    df['tenure_group'] = pd.cut(df['tenure'],
                                bins= [0, 12, 24, 48, 60, 72],
                                labels=['0-1 Tahun', '1-2 Tahun', '2-4 Tahun', '4-5 Tahun', '>5 Tahun'])
    
    return df

# Testing 
try:
    df = load_data()
    st.success("Data berhasil dimuat!") # Ini untuk testing awal, nanti bisa dihapus
except FileNotFoundError:
    st.error("⚠️ File data tidak ditemukan. Periksa kembali nama file di folder data/clean/ Anda.")
    st.stop()

# ===============================
#       SIDEBAR FILTER
# ===============================
st.sidebar.header("Filter Dashboard")

# Contract Filter
contract_list = ['All'] + list(df['Contract'].unique())
selected_contract = st.sidebar.selectbox("Select Contract Type", contract_list)

# Internet Service Filter
internetservice_list = ['All'] + list(df['InternetService'].unique())
selected_internetservice = st.sidebar.selectbox("Select Internet Service", internetservice_list)

# Filtering Logic
df_filtered = df.copy()

if selected_contract != 'All' :
    df_filtered = df_filtered[df_filtered['Contract'] == selected_contract]
if selected_internetservice != 'All' :
    df_filtered = df_filtered[df_filtered['InternetService'] == selected_internetservice]

# ===============================
#     KEY MATRIX (KPI CARDS)
# ===============================
total_customers = len(df_filtered)

# Calculate Churn Rate (Ratio of percentage of customers who Churn == 'Yes')
if total_customers > 0 :
    churn_count = len(df_filtered[df_filtered['Churn'] == 'Yes'])
    churn_rate = churn_count / total_customers * 100
    avg_monthly_charges = df_filtered['MonthlyCharges'].mean()
    avg_tenure = df_filtered['tenure'].mean()
else :
    churn_rate = 0.0
    avg_monthly_charges = 0.0
    avg_tenure = 0.0

# KPI Layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Total Customers',value=f'{total_customers:,}')

with col2:
    st.metric(
        label='Churn Rate',
        value=f'{churn_rate:.2f}%',
        delta=f'{churn_rate:.1f}% Risk' if churn_rate > 20 else None,
        delta_color='inverse'
    )

with col3:
    st.metric(label='Average Monthly Charges', value=f'${avg_monthly_charges:.2f}')

with col4:
    st.metric(label='Average Tenure (Month)', value=f'{avg_tenure:.1f} Month') 

st.markdown("---")

# ==========================================
#   SECTION GRAFIK (UNIVARIAT & BIVARIAT)
# ==========================================

st.subheader("Visual Analysis of Distribution & Churn Factors")

tab1, tab2 = st.tabs(["Data Distribution (Univariate)", "Churn Triggers (Bivariate)"])

# ------------------------------------------
#            UNIVARIATE ANALYSIS
# ------------------------------------------
with tab1:
    col_a, col_b =st.columns(2)

    with col_a :
        st.markdown("<h4 style='text-align: center;'>Churn Status Proportion</h4", unsafe_allow_html=True)
        churn_counts = df_filtered['Churn'].value_counts()

        fig_donut = go.Figure(data=[go.Pie(
            labels=churn_counts.index,
            values=churn_counts.values,
            hole=.5,
            marker_colors=['#4C72B0','#C44E52'] # Blue for 'No' and Red for 'Yeahhh'
        )])
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height= 350)
        st.plotly_chart(fig_donut, use_container_width=True)
    with col_b :
        st.markdown("<h4 style='text-align: center;'>Monthly Charge Distribution</h4", unsafe_allow_html=True)
        fig_hist = px.histogram(
            df_filtered,
            x='MonthlyCharges',
            color='Churn',
            color_discrete_map={'No': '#4C72B0', 'Yes': '#C44E52'},
            marginal='box',
            nbins=30
        )
        fig_hist.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), yaxis_title='Total Customer')
        st.plotly_chart(fig_hist, use_container_width=True)


# ------------------------------------------
#           BIVARIATE ANALYSIS
# ------------------------------------------
with tab2:
    st.markdown('##### Analysis of the Relationship between Customer Characteristics and Churn')
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("<h4 style='text-align: center;'>Churn by Contract Type</h4>", unsafe_allow_html=True)
        fig_contract = px.histogram(
            df_filtered,
            x='Contract',
            color='Churn',
            barmode='group',
            color_discrete_map={'No' : '#4C72B0', 'Yes': '#C44E52'}
        )
        fig_contract.update_traces(
            texttemplate='%{y}', 
            textposition='outside',
            hovertemplate="Status: %{legendgroup}<br>Jumlah: %{y}<br>Kategori: %{x}"
        )
        fig_contract.update_layout(height=350, yaxis_title='Total Customers')
        st.plotly_chart(fig_contract, use_container_width=True)

    with col_d:
        st.markdown("<h4 style='text-align: center;'>Churn by Payment Method</h4>", unsafe_allow_html=True)
        fig_payment = px.histogram(
            df_filtered,
            x='PaymentMethod',
            color='Churn',
            barmode='group',
            color_discrete_map={'No' : '#4C72B0', 'Yes': '#C44E52'}
        )
        fig_payment.update_traces(
            texttemplate='%{y}', 
            textposition='outside',
            hovertemplate="Status: %{legendgroup}<br>Jumlah: %{y}<br>Kategori: %{x}"
        )   
        fig_payment.update_layout(height=350, yaxis_title='Total Customers')
        st.plotly_chart(fig_payment, use_container_width=True)
    
# ==========================================
#    SECTION MULTIVARIATE (HEATMAP RISK)
# ==========================================
st.markdown('---')
st.subheader('High-Level Risk Analysis (Multivariate)')
st.markdown('Customer Churn Analysis Based on Tenure and Internet Services')

if 'tenure_group' in df_filtered.columns and 'InternetService' in df_filtered.columns :
    pivot_data = df_filtered.pivot_table(
        index='InternetService',
        columns='tenure_group',
        values='Churn',
        aggfunc=lambda x: (x == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
    )

    fig_heatmap = px.imshow(
        pivot_data,
        text_auto='.1f',
        color_continuous_scale='YlOrRd',
        labels=dict(x='Subscription Period (Tenure Group)', y='Internet Service', color='Ratio Churn (%)')
    )

    fig_heatmap.update_layout(
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.warning("⚠️ Column `tenure_group` or `InternetService` was not found to create Heatmap.")

# ==========================================
#    STRATEGIC BUSINESS RECOMMENDATIONS
# ==========================================
st.markdown('---')
st.subheader('Data-Driven Business Recommendations (Actionable Insights)')

col_rec1, col_rec2, col_rec3 = st.columns(3)

with col_rec1 :
    st.info(" **Contract Migration Strategy** ")
    st.markdown("""
    * **Masalah**: Pelanggan *Month-to-month* memiliki rasio churn sangat tinggi (**42.71%**).
    * **Solusi**: Tim Marketing harus memberikan insentif berupa potongan harga atau bonus kuota bagi pelanggan bulanan yang bersedia migrasi ke kontrak 1 atau 2 tahun.
    """)

with col_rec2:
    st.error(" **Evaluasi Pengguna Fiber Optic** ")
    st.markdown("""
    * **Masalah**: Risiko churn pada pengguna *Fiber optic* baru (0-1 tahun) sangat kritis, mencapai **69.9%**.
    * **Solusi**: Lakukan audit kualitas jaringan di area tertentu, perbaiki skema harga paket promosi, dan berikan layanan penanganan gangguan prioritas (*fast-track*) di tahun pertama.
    """)

with col_rec3:
    st.success(" **Otomatisasi Sistem Pembayaran** ")
    st.markdown("""
    * **Masalah**: Pengguna metode *Electronic check* menyumbang angka churn tertinggi sebesar **45.29%**.
    * **Solusi**: Berikan potongan biaya bulanan (misal senilai $2) jika pelanggan bersedia mendaftarkan rekening atau kartu kredit mereka ke sistem pembayaran otomatis (*Auto-pay*).
    """)