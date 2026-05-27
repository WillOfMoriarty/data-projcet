import pandas as pd
import random
from faker import Faker
from datetime import timedelta

fake = Faker()

users = pd.read_csv("data/raw/users.csv")
events = pd.read_csv("data/raw/events.csv")

subscriptions = []
subscription_id = 1

# group events for fast lookup
user_event_group = events.groupby("user_id")["event_name"].apply(list).to_dict()

for _, user in users.iterrows():
    
    user_id = user["user_id"]
    user_events = user_event_group.get(user_id, [])
    
    # ----------------------------
    # ENGAGEMENT SCORE
    # ----------------------------
    score = 0
    
    score += user_events.count("task_created") * 1
    score += user_events.count("feature_used") * 2
    score += user_events.count("workspace_created") * 3
    score += user_events.count("first_task_created") * 2
    
    # ----------------------------
    # SEGMENT BASED PROBABILITY
    # ----------------------------
    if score < 3:
        conversion_prob = 0.03  # casual
    elif score < 8:
        conversion_prob = 0.15  # power user
    else:
        conversion_prob = 0.45  # sticky user
    
    # traffic source modifier
    if user["traffic_source"] == "Referral":
        conversion_prob *= 1.3
    elif user["traffic_source"] == "Google Ads":
        conversion_prob *= 0.9
    
    # ----------------------------
    # DECISION: CONVERT OR NOT
    # ----------------------------
    if random.random() < conversion_prob:
        
        start_date = fake.date_between(start_date="-60d", end_date="today")
        
        # churn logic
        if score < 5:
            status = "canceled"
        else:
            status = "active" if random.random() < 0.8 else "canceled"
        
        subscriptions.append({
            "subscription_id": subscription_id,
            "user_id": user_id,
            "plan": "pro",
            "monthly_revenue": 20,
            "status": status,
            "start_date": start_date,
            "churn_date": None if status == "active" else fake.date_between(start_date=start_date, end_date="today")
        })
        
        subscription_id += 1


df = pd.DataFrame(subscriptions)
df.to_csv("data/raw/subscriptions.csv", index=False)

print(f"Subscriptions generated: {len(df)}")