import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & ASSASET PATH
# ==========================================
st.set_page_config(page_title="Customer Churn & Revenue Analytics", layout="wide", initial_sidebar_state="expanded")

DATA_DIR = r"C:\VSCode\customer-churn-analytics\data\processed"

@st.cache_data
def load_data():
    # Load 5 tabel bersih
    cust = pd.read_csv(os.path.join(DATA_DIR, "customers_clean.csv"))
    sub = pd.read_csv(os.path.join(DATA_DIR, "subscriptions_clean.csv"))
    pay = pd.read_csv(os.path.join(DATA_DIR, "payments_clean.csv"))
    prod = pd.read_csv(os.path.join(DATA_DIR, "product_usage_clean.csv"))
    ticket = pd.read_csv(os.path.join(DATA_DIR, "support_tickets_clean.csv"))
    
    # Konversi kolom datetime
    cust['signup_date'] = pd.to_datetime(cust['signup_date'])
    cust['last_login_date'] = pd.to_datetime(cust['last_login_date'])
    sub['start_date'] = pd.to_datetime(sub['start_date'])
    sub['end_date'] = pd.to_datetime(sub['end_date'])
    pay['payment_date'] = pd.to_datetime(pay['payment_date'])
    prod['usage_date'] = pd.to_datetime(prod['usage_date'])
    ticket['created_date'] = pd.to_datetime(ticket['created_date'])
    
    return cust, sub, pay, prod, ticket

try:
    df_cust, df_sub, df_pay, df_prod, df_ticket = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Pastikan file CSV ada di {DATA_DIR}. Error: {e}")
    st.stop()

# Master Merge untuk kemudahan filter global berbasis Customer
df_master = pd.merge(df_cust, df_sub, on="customer_id", how="inner")

# ==========================================
# 2. GLOBAL SIDEBAR FILTERS
# ==========================================
st.sidebar.title("Filter Dashboard")

all_countries = sorted(df_master['country'].unique())
selected_countries = st.sidebar.multiselect("Negara", all_countries, default=all_countries)

all_plans = sorted(df_master['plan'].unique())
selected_plans = st.sidebar.multiselect("Paket (Plan)", all_plans, default=all_plans)

all_sizes = sorted(df_master['company_size'].unique())
selected_sizes = st.sidebar.multiselect("Ukuran Perusahaan", all_sizes, default=all_sizes)

all_industries = sorted(df_master['industry'].unique())
selected_industries = st.sidebar.multiselect("Industri", all_industries, default=all_industries)

# Terapkan filter ke dataframe utama
filtered_master = df_master[
    (df_master['country'].isin(selected_countries)) &
    (df_master['plan'].isin(selected_plans)) &
    (df_master['company_size'].isin(selected_sizes)) &
    (df_master['industry'].isin(selected_industries))
]
filtered_cust_ids = filtered_master['customer_id'].unique()

# Turunan filter ke tabel transaksi
filtered_pay = df_pay[df_pay['customer_id'].isin(filtered_cust_ids)]
filtered_prod = df_prod[df_prod['customer_id'].isin(filtered_cust_ids)]
filtered_ticket = df_ticket[df_ticket['customer_id'].isin(filtered_cust_ids)]

# ==========================================
# 3. NAVIGASI HALAMAN (TABS)
# ==========================================
tabs = st.tabs([
    "📈 Executive Overview", 
    "👥 Customer & Churn", 
    "💰 Revenue Analytics", 
    "🛠️  Support & Engagement"
])

# ------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ------------------------------------------
with tabs[0]:
    st.header("Executive Overview")
    
    # Hitung KPI
    total_cust = len(filtered_master)
    active_cust = len(filtered_master[filtered_master['status'] == 'Active'])
    churn_cust = len(filtered_master[filtered_master['status'] == 'Churned'])
    churn_rate = (churn_cust / total_cust * 100) if total_cust > 0 else 0
    retention_rate = 100 - churn_rate
    
    total_rev = filtered_pay[filtered_pay['payment_status'] == 'Paid']['amount'].sum()
    rev_loss = filtered_pay[filtered_pay['payment_status'] == 'Unpaid']['amount'].sum() # Estimasi loss dari unpaid/refunded
    
    # Baris KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric("Total Customers", f"{total_cust:,}")
    kpi2.metric("Active Customers", f"{active_cust:,}")
    kpi3.metric("Churn Rate", f"{churn_rate:.2f}%")
    kpi4.metric("Retention Rate", f"{retention_rate:.2f}%")
    kpi5.metric("Total Revenue", f"${total_rev:,}")
    kpi6.metric("Revenue Loss", f"${rev_loss:,}")
    
    st.markdown("---")
    
    # Tren Bulanan
    col1, col2 = st.columns(2)
    with col1:
        # Monthly Revenue Trend
        pay_trend = filtered_pay[filtered_pay['payment_status'] == 'Paid'].copy()
        pay_trend['Month'] = pay_trend['payment_date'].dt.to_period('M').astype(str)
        rev_trend_df = pay_trend.groupby('Month')['amount'].sum().reset_index()
        fig_rev_trend = px.line(rev_trend_df, x='Month', y='amount', title="Monthly Revenue Trend", markers=True)
        st.plotly_chart(fig_rev_trend, use_container_width=True)
        
    with col2:
        # Monthly Churn Trend
        churn_trend = filtered_master[filtered_master['status'] == 'Churned'].copy()
        churn_trend['Month'] = churn_trend['end_date'].dt.to_period('M').astype(str)
        churn_trend_df = churn_trend.groupby('Month').size().reset_index(name='Churn Count')
        fig_churn_trend = px.line(churn_trend_df, x='Month', y='Churn Count', title="Monthly Churn Trend", markers=True, color_discrete_sequence=['red'])
        st.plotly_chart(fig_churn_trend, use_container_width=True)

    # Segmentasi Bar Charts
    col3, col4 = st.columns(2)
    with col3:
        rev_by_plan = filtered_master.groupby('plan')['monthly_fee'].sum().reset_index()
        fig_rev_plan = px.bar(rev_by_plan, x='plan', y='monthly_fee', title="Revenue Capacity by Plan Tier", labels={'monthly_fee':'Total Fee'})
        st.plotly_chart(fig_rev_plan, use_container_width=True)
    with col4:
        churn_by_plan = filtered_master.groupby(['plan', 'status']).size().reset_index(name='Count')
        fig_churn_plan = px.bar(churn_by_plan, x='plan', y='Count', color='status', barmode='group', title="Churn vs Active Status by Plan")
        st.plotly_chart(fig_churn_plan, use_container_width=True)

# ------------------------------------------
# PAGE 2: CUSTOMER & CHURN ANALYSIS
# ------------------------------------------
with tabs[1]:
    st.header("Customer & Churn Deep-Dive")
    
    col1, col2 = st.columns(2)
    with col1:
        churn_by_size = filtered_master.groupby(['company_size', 'status']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(churn_by_size, x='company_size', y='Count', color='status', barmode='stack', title="Churn by Company Size"), use_container_width=True)
        
        cust_by_ind = filtered_master.groupby('industry').size().reset_index(name='Count')
        st.plotly_chart(px.pie(cust_by_ind, values='Count', names='industry', title="Customer Distribution by Industry"), use_container_width=True)
        
    with col2:
        churn_by_acq = filtered_master.groupby(['acquisition_channel', 'status']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(churn_by_acq, y='acquisition_channel', x='Count', color='status', barmode='group', orientation='h', title="Churn by Acquisition Channel"), use_container_width=True)
        
        cust_by_country = filtered_master.groupby('country').size().reset_index(name='Count')
        st.plotly_chart(px.pie(cust_by_country, values='Count', names='country', title="Customer Distribution by Country", hole=0.4), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(px.histogram(filtered_master, x='tenure_months', color='status', nbins=20, title="Tenure Lifespan Distribution (Months)"), use_container_width=True)
    with col4:
        # Gabungkan penggunaan fitur dengan status churn via customer_id
        feat_adoption = pd.merge(filtered_prod, filtered_master[['customer_id', 'status']], on='customer_id', how='inner')
        feat_df = feat_adoption.groupby(['feature_used', 'status']).size().reset_index(name='Usage Count')
        st.plotly_chart(px.bar(feat_df, x='feature_used', y='Usage Count', color='status', barmode='group', title="Feature Adoption by Status"), use_container_width=True)

    # Key Insight Section
    st.subheader("💡 Automated Key Insights")
    ins1, ins2, ins3 = st.columns(3)
    
    # Hitung rasio churn tertinggi per segmen
    def get_max_churn_segment(column_name):
        df_pct = pd.crosstab(filtered_master[column_name], filtered_master['status'], normalize='index') * 100
        if 'Churned' in df_pct.columns:
            return df_pct['Churned'].idxmax(), df_pct['Churned'].max()
        return "N/A", 0

    size_max, size_val = get_max_churn_segment('company_size')
    chan_max, chan_val = get_max_churn_segment('acquisition_channel')
    ind_max, ind_val = get_max_churn_segment('industry')

    ins1.info(f"**Highest Churn Risk Segments:**\n* **Size:** {size_max} ({size_val:.1f}% Churn Rate)\n* **Channel:** {chan_max} ({chan_val:.1f}%)")
    
    # Mencari retensi terbaik
    def get_max_retention_segment(column_name):
        df_pct = pd.crosstab(filtered_master[column_name], filtered_master['status'], normalize='index') * 100
        if 'Active' in df_pct.columns:
            return df_pct['Active'].idxmax(), df_pct['Active'].max()
        return "N/A", 0
        
    ret_country, ret_val = get_max_retention_segment('country')
    ins2.success(f"**Highest Retention Anchor:**\n* **Country:** {ret_country} ({ret_val:.1f}% Active Retention)")
    
    # Hitung loss tertinggi
    loss_by_ind = filtered_pay[filtered_pay['payment_status'] == 'Unpaid'].merge(filtered_master[['customer_id', 'industry']], on='customer_id')
    if not loss_by_ind.empty:
        top_loss_ind = loss_by_ind.groupby('industry')['amount'].sum().idxmax()
        top_loss_val = loss_by_ind.groupby('industry')['amount'].sum().max()

        ins3.warning(
            f"Highest Revenue Loss Sector:\n"
            f"* Industry: {top_loss_ind} (${top_loss_val:,} Lost due to unpaid payments)"
        )
    else:
        ins3.warning(
            "Highest Revenue Loss Sector:\n"
            "* Tidak ada data kerugian pembayaran yang terdeteksi."
        )

# ------------------------------------------
# PAGE 3: REVENUE ANALYTICS
# ------------------------------------------
with tabs[2]:
    st.header("Revenue & ARPU Deep-Dive")

    # KPI Baru untuk Halaman Keuangan
    paid_payments = filtered_pay[filtered_pay["payment_status"] == "Paid"]
    total_rev_p3 = paid_payments["amount"].sum()
    arpu = (total_rev_p3 / total_cust) if total_cust > 0 else 0

    total_loss_p3 = filtered_pay[
        filtered_pay["payment_status"] == "Unpaid"
    ]["amount"].sum()

    loss_rate = (
        total_loss_p3 / (total_rev_p3 + total_loss_p3) * 100
        if (total_rev_p3 + total_loss_p3) > 0
        else 0
    )

    avg_lifetime = filtered_master["tenure_months"].mean()

    rkpi1, rkpi2, rkpi3 = st.columns(3)

    rkpi1.metric("Average Revenue Per User (ARPU)", f"${arpu:.2f}")
    rkpi2.metric("Revenue Loss Rate", f"{loss_rate:.2f}%")
    rkpi3.metric("Avg Customer Lifetime", f"{avg_lifetime:.1f} Months")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        rev_plan = (
            paid_payments.merge(
                filtered_master[["customer_id", "plan"]],
                on="customer_id",
            )
            .groupby("plan")["amount"]
            .sum()
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                rev_plan,
                x="plan",
                y="amount",
                title="Revenue by Plan Tier",
                color="plan",
            ),
            use_container_width=True,
        )

    with col2:
        rev_size = (
            paid_payments.merge(
                filtered_master[["customer_id", "company_size"]],
                on="customer_id",
            )
            .groupby("company_size")["amount"]
            .sum()
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                rev_size,
                x="company_size",
                y="amount",
                title="Revenue by Company Size",
                color="company_size",
            ),
            use_container_width=True,
        )

    with col3:
        rev_ind = (
            paid_payments.merge(
                filtered_master[["customer_id", "industry"]],
                on="customer_id",
            )
            .groupby("industry")["amount"]
            .sum()
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                rev_ind,
                x="amount",
                y="industry",
                orientation="h",
                title="Revenue by Industry",
            ),
            use_container_width=True,
        )

    col4, col5 = st.columns(2)

    with col4:
        arpu_country = (
            filtered_master.groupby("country")
            .apply(
                lambda x: (
                    filtered_pay[
                        (filtered_pay["customer_id"].isin(x["customer_id"]))
                        & (filtered_pay["payment_status"] == "Paid")
                    ]["amount"].sum()
                    / len(x)
                    if len(x) > 0
                    else 0
                )
            )
            .reset_index(name="ARPU")
        )

        st.plotly_chart(
            px.bar(
                arpu_country,
                x="country",
                y="ARPU",
                title="ARPU by Country",
            ),
            use_container_width=True,
        )

    with col5:
        loss_df = filtered_pay[
            filtered_pay["payment_status"].isin(["Unpaid", "Refunded"])
        ].merge(
            filtered_master[["customer_id", "company_size"]],
            on="customer_id",
        )

        loss_seg = (
            loss_df.groupby(["company_size", "payment_status"])["amount"]
            .sum()
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                loss_seg,
                x="company_size",
                y="amount",
                color="payment_status",
                title="Revenue Loss Breakdown by Segment",
            ),
            use_container_width=True,
        )

# ------------------------------------------
# PAGE 4: SUPPORT & PRODUCT ENGAGEMENT
# ------------------------------------------
with tabs[3]:
    st.header("Support Tickets & Product Engagement")

    total_tickets = len(filtered_ticket)
    unique_complainers = filtered_ticket["customer_id"].nunique()
    avg_ticket_per_cust = (
        total_tickets / total_cust if total_cust > 0 else 0
    )
    avg_resolution = filtered_ticket["resolution_time_hours"].mean()

    total_active_users = (
        filtered_master[filtered_master["status"] == "Active"]["customer_id"]
        .nunique()
    )

    users_with_features = filtered_prod["customer_id"].nunique()

    feature_adoption_rate = (
        users_with_features / total_cust * 100
        if total_cust > 0
        else 0
    )

    ekpi1, ekpi2, ekpi3 = st.columns(3)

    ekpi1.metric(
        "Avg Tickets per Customer",
        f"{avg_ticket_per_cust:.2f}",
    )
    ekpi2.metric(
        "Avg Resolution Time",
        f"{avg_resolution:.1f} Hours",
    )
    ekpi3.metric(
        "Feature Adoption Rate",
        f"{feature_adoption_rate:.1f}%",
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        ticket_status_df = (
            filtered_ticket.groupby("ticket_status")
            .size()
            .reset_index(name="Count")
        )

        st.plotly_chart(
            px.bar(
                ticket_status_df,
                x="ticket_status",
                y="Count",
                color="ticket_status",
                title="Average Tickets by Status (Volume)",
            ),
            use_container_width=True,
        )

        issue_df = (
            filtered_ticket.groupby("issue_type")
            .size()
            .reset_index(name="Ticket Count")
        )

        st.plotly_chart(
            px.pie(
                issue_df,
                values="Ticket Count",
                names="issue_type",
                title="Issue Type Breakdown",
            ),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            px.histogram(
                filtered_ticket,
                x="resolution_time_hours",
                nbins=30,
                color_discrete_sequence=["orange"],
                title="Resolution Time Distribution (Hours)",
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            px.box(
                filtered_prod,
                x="feature_used",
                y="session_duration",
                title="Session Duration Distribution by Feature",
            ),
            use_container_width=True,
        )

    st.markdown("---")

    st.subheader("Correlation Analysis: Ticket Volume vs. Churn Status")

    ticket_counts = (
        filtered_ticket.groupby("customer_id")
        .size()
        .reset_index(name="ticket_count")
    )

    cust_churn_status = filtered_master[
        ["customer_id", "status"]
    ]

    corr_df = (
        pd.merge(
            ticket_counts,
            cust_churn_status,
            on="customer_id",
            how="right",
        )
        .fillna(0)
    )

    st.plotly_chart(
        px.box(
            corr_df,
            x="status",
            y="ticket_count",
            color="status",
            title="Apakah User yang Churn Mengirimkan Komplain Lebih Banyak?",
        ),
        use_container_width=True,
    )