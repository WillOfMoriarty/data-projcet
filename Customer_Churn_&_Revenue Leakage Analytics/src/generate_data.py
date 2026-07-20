import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta
import random
import os

# =====================================================
# CONFIG
# =====================================================

fake = Faker()

np.random.seed(42)
random.seed(42)

N_CUSTOMERS = 20000
ANALYSIS_DATE = pd.Timestamp("2026-06-01")

# PERBAIKAN: Mengunci path absolut ke dalam folder proyek utama
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# MASTER DATA
# =====================================================

countries = ["USA", "Canada", "UK", "Germany", "Australia", "Singapore", "Indonesia"]
genders = ["Male", "Female"]
channels = ["Organic", "Google Ads", "LinkedIn", "Referral", "Facebook Ads"]
industries = ["Technology", "Finance", "Healthcare", "Retail", "Education", "Manufacturing"]

plans = {
    "Basic": 49,
    "Standard": 99,
    "Premium": 199,
    "Enterprise": 499
}

features = ["Dashboard", "Analytics", "Export", "API", "Automation"]
issue_types = ["Bug", "Billing", "Feature Request", "Login Issue", "Performance"]

# =====================================================
# 1. CUSTOMERS
# =====================================================

print("Generating customers...")
customers = []

for customer_id in range(1, N_CUSTOMERS + 1):
    signup_date = fake.date_between(start_date="-3y", end_date="-30d")
    customers.append({
        "customer_id": customer_id,
        "signup_date": signup_date,
        "country": random.choice(countries),
        "age": random.randint(18, 65),
        "gender": random.choice(genders),
        "acquisition_channel": random.choice(channels),
        "company_size": random.choices(["Small", "Medium", "Large"], weights=[0.6, 0.3, 0.1])[0],
        "industry": random.choice(industries)
    })

customers_df = pd.DataFrame(customers)

# =====================================================
# 2. SUBSCRIPTIONS
# =====================================================

print("Generating subscriptions...")
subscriptions = []

for _, row in customers_df.iterrows():
    plan = random.choices(["Basic", "Standard", "Premium", "Enterprise"], weights=[40, 30, 20, 10])[0]
    contract_type = random.choices(["Monthly", "Annual"], weights=[70, 30])[0]
    start_date = pd.Timestamp(row["signup_date"])

    subscriptions.append({
        "subscription_id": len(subscriptions) + 1,
        "customer_id": row["customer_id"],
        "plan": plan,
        "contract_type": contract_type,
        "start_date": start_date,
        "end_date": None,
        "status": "Pending",
        "monthly_fee": plans[plan]
    })

subscriptions_df = pd.DataFrame(subscriptions)

# =====================================================
# 3. PRODUCT USAGE
# =====================================================

print("Generating usage data...")
usage_rows = []
usage_id = 1

for _, sub in subscriptions_df.iterrows():
    plan = sub["plan"]
    if plan == "Enterprise":
        avg_usage = 35
    elif plan == "Premium":
        avg_usage = 25
    elif plan == "Standard":
        avg_usage = 18
    else:
        avg_usage = 10

    n_records = np.random.poisson(avg_usage)

    for _ in range(n_records):
        usage_rows.append({
            "usage_id": usage_id,
            "customer_id": sub["customer_id"],
            # PERBAIKAN: Mengonversi sub["start_date"] menjadi format objek .date() agar dipahami oleh Faker
            "usage_date": fake.date_between(start_date=sub["start_date"].date(), end_date=ANALYSIS_DATE.date()),
            "login_count": np.random.poisson(5),
            "session_duration": round(max(1, np.random.normal(45, 15)), 2),
            "feature_used": random.choice(features)
        })
        usage_id += 1

usage_df = pd.DataFrame(usage_rows)

# =====================================================
# 4. SUPPORT TICKETS
# =====================================================

print("Generating tickets...")
ticket_rows = []
ticket_id = 1

for _, sub in subscriptions_df.iterrows():
    if sub["plan"] == "Basic":
        avg_ticket = 3
    else:
        avg_ticket = 2

    n_tickets = np.random.poisson(avg_ticket)

    for _ in range(n_tickets):
        ticket_rows.append({
            "ticket_id": ticket_id,
            "customer_id": sub["customer_id"],
            # PERBAIKAN: Mengonversi sub["start_date"] menjadi format objek .date() agar dipahami oleh Faker
            "created_date": fake.date_between(start_date=sub["start_date"].date(), end_date=ANALYSIS_DATE.date()),
            "issue_type": random.choice(issue_types),
            "resolution_time_hours": round(abs(np.random.normal(24, 8)), 2),
            "ticket_status": random.choice(["Resolved", "Closed"])
        })
        ticket_id += 1

tickets_df = pd.DataFrame(ticket_rows)

# =====================================================
# 5. CHURN CALCULATION
# =====================================================

print("Calculating churn...")

usage_summary = (
    usage_df
    .groupby("customer_id")
    .agg(avg_login=("login_count", "mean"), last_login_date=("usage_date", "max"))
    .reset_index()
)

ticket_summary = (
    tickets_df
    .groupby("customer_id")
    .size()
    .reset_index(name="ticket_count")
)

# PERBAIKAN: Menambahkan .merge(customers_df) agar kolom 'company_size' masuk ke tabel perhitungan churn
customer_health = (
    subscriptions_df
    .merge(usage_summary, on="customer_id", how="left")
    .merge(ticket_summary, on="customer_id", how="left")
    .merge(customers_df[["customer_id", "company_size"]], on="customer_id", how="left")
)

customer_health["avg_login"] = customer_health["avg_login"].fillna(0)
customer_health["ticket_count"] = customer_health["ticket_count"].fillna(0)

updated_subs = []

for _, row in customer_health.iterrows():
    churn_prob = 0.05

    if row["avg_login"] < 3:
        churn_prob += 0.60
    if row["ticket_count"] > 3:
        churn_prob += 0.50
    if row["plan"] == "Basic":
        churn_prob += 0.35
    if row["plan"] == "Enterprise":
        churn_prob -= 0.08
    if row["company_size"] == "Small":
        churn_prob += 0.20
    if row["contract_type"] == "Annual":
        churn_prob -= 0.10

    churn_prob = min(max(churn_prob, 0.01), 0.95)
    churned = (np.random.rand() < churn_prob)
    end_date = None

    if churned:
        end_date = row["start_date"] + timedelta(days=random.randint(30, 700))
        if end_date > ANALYSIS_DATE:
            churned = False
            end_date = None

    status = "Churned" if churned else "Active"
    
    # PERBAIKAN: Memastikan end_date atau ANALYSIS_DATE dikonversi ke Timestamp sebelum dikurangi objek start_date
    ref_date = pd.Timestamp(end_date) if end_date else ANALYSIS_DATE
    tenure_months = ((ref_date - row["start_date"]).days) // 30

    updated_subs.append({
        "subscription_id": row["subscription_id"],
        "customer_id": row["customer_id"],
        "plan": row["plan"],
        "contract_type": row["contract_type"],
        "start_date": row["start_date"],
        "end_date": end_date.date() if isinstance(end_date, pd.Timestamp) or hasattr(end_date, 'date') and end_date else end_date,
        "status": status,
        "monthly_fee": row["monthly_fee"],
        "tenure_months": max(0, tenure_months)
    })

subscriptions_df = pd.DataFrame(updated_subs)

# =====================================================
# LAST LOGIN
# =====================================================

customers_df = customers_df.merge(
    usage_summary[["customer_id", "last_login_date"]],
    on="customer_id",
    how="left"
)

# =====================================================
# 6. PAYMENTS
# =====================================================

print("Generating payments...")
payments = []
payment_id = 1

for _, sub in subscriptions_df.iterrows():
    start = pd.Timestamp(sub["start_date"])
    end = pd.Timestamp(sub["end_date"]) if pd.notnull(sub["end_date"]) else ANALYSIS_DATE

    months = (end.year - start.year) * 12 + end.month - start.month

    for m in range(months + 1):
        payment_date = start + pd.DateOffset(months=m)
        if payment_date > ANALYSIS_DATE:
            break

        payments.append({
            "payment_id": payment_id,
            "customer_id": sub["customer_id"],
            "payment_date": payment_date.date(),
            "amount": sub["monthly_fee"],
            "payment_status": np.random.choice(["Paid", "Failed", "Refunded"], p=[0.92, 0.06, 0.02]),
            "payment_method": random.choice(["Credit Card", "PayPal", "Bank Transfer"])
        })
        payment_id += 1

payments_df = pd.DataFrame(payments)

# =====================================================
# SAVE FILES (PERBAIKAN: Menyambung kode yang terpotong)
# =====================================================

print(f"Saving CSV files to: {OUTPUT_DIR}")
customers_df.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
subscriptions_df.to_csv(os.path.join(OUTPUT_DIR, "subscriptions.csv"), index=False)
payments_df.to_csv(os.path.join(OUTPUT_DIR, "payments.csv"), index=False)
usage_df.to_csv(os.path.join(OUTPUT_DIR, "product_usage.csv"), index=False)
tickets_df.to_csv(os.path.join(OUTPUT_DIR, "support_tickets.csv"), index=False)

print("================================")
print("Dataset generated successfully!")
print("================================")
