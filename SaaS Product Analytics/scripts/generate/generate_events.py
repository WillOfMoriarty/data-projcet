import pandas as pd
import random
from faker import Faker
from datetime import timedelta

fake = Faker()

users = pd.read_csv("data/raw/users.csv")
sesions = pd.read_csv("data/raw/sessions.csv")

events = []
event_id = 1

sesions_map = sesions[['session_id', 'user_id', 'session_start', 'session_end']]

for _, session in sesions_map.iterrows():
    user_id = session['user_id']
    session_id = session["session_id"]

    session_start = pd.to_datetime(session["session_start"])
    session_end = pd.to_datetime(session['session_end'])

    duration_minutes = int((session_end - session_start).total_seconds() / 60)

    # ----------------------------
    # USER BASED BEHAVIOR
    # ----------------------------
    user = users[users['user_id'] == user_id].iloc[0]

    if user["traffic_source"] == "Organic":
        engagement_multiplier = 1.2
    elif user["traffic_source"] == "Google Ads":
        engagement_multiplier = 0.8
    elif user["traffic_source"] == "Referral":
        engagement_multiplier = 1.5
    else:
        engagement_multiplier = 1.0

    # ----------------------------
    # EVENT FLOW DECISION
    # ----------------------------
    base_events = ['landing_page_view']

    if random.random() < 0.9:
        base_events.append("signup_started")
    
    if random.random() < 0.7:
        base_events.append("signup_completed")
    
    if random.random() < 0.5 * engagement_multiplier:
        base_events.append("workspace_created")
    
    if random.random() < 0.4 * engagement_multiplier:
        base_events.append("first_task_created")

    # ----------------------------
    # ENGAGEMENT LOOP
    # ----------------------------
    num_tasks = random.randint(0, int(5 * engagement_multiplier))
    
    for _ in range(num_tasks):
        base_events.append("task_created")
    
    if random.random() < 0.6 * engagement_multiplier:
        base_events.append("feature_used")
    
    # ----------------------------
    # MONETIZATION
    # ----------------------------
    if random.random() < 0.25 * engagement_multiplier:
        base_events.append("subscription_started")
        
        if random.random() < 0.8:
            base_events.append("payment_completed")
    
    # ----------------------------
    # TIMESTAMP DISTRIBUTION
    # ----------------------------
    num_events = len(base_events)
    
    for i, event_name in enumerate(base_events):
        
        event_time = session_start + timedelta(
            minutes=random.randint(0, max(1, duration_minutes))
        )
        
        events.append({
            "event_id": event_id,
            "user_id": user_id,
            "session_id": session_id,
            "event_timestamp": event_time,
            "event_name": event_name,
            "feature_name": event_name if event_name in ["task_created", "feature_used"] else None
        })
        
        event_id += 1


df = pd.DataFrame(events)
df.to_csv("data/raw/events.csv", index=False)

print(f"Events generated: {len(df)}")