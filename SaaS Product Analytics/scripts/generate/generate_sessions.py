import pandas as pd
import random
from faker import Faker
from datetime import timedelta

fake = Faker()

users = pd.read_csv("data/raw/users.csv")

sessions = []
session_id = 1

for _, user in users.iterrows():
    # ----------------------------
    #   USER SEGMENT SIMULATION
    # ----------------------------
    segment_roll = random.random()

    if segment_roll < 0.5:
        user_type ='casual'
        num_sessions = random.randint(1, 2)
        session_duration_range = (5, 20)

    elif segment_roll < 0.85:
        user_type ='power'
        num_sessions = random.randint(3, 6)
        session_duration_range = (15, 45)
    
    else:
        user_type = 'sticky'
        num_sessions = random.randint(5, 10)
        session_duration_range = (30, 90)

    # ----------------------------
    #      GENERATE SESSIONS
    # ----------------------------
    for _ in range(num_sessions):
        session_start = fake.date_time_between(start_date='-90d', end_date='now')

        duration = random.randint(
            session_duration_range[0],
            session_duration_range[1]
        )

        session_end = session_start + timedelta(minutes=duration)

        sessions.append({
            "session_id": session_id,
            "user_id": user["user_id"],
            "session_start": session_start,
            "session_end": session_end,
            "session_duration_min": duration,
            "user_type": user_type
        })

        session_id += 1

df = pd.DataFrame(sessions)
df.to_csv("data/raw/sessions.csv", index=False)

print(f"Sessions generated : {len(df)}")