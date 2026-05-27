import pandas as pd
import random
from faker import Faker

fake = Faker()

NUM_USERS = 1000

traffic_sources = ["Organic", "Google Ads", "Referral", "LinkedIn Ads", "YouTube"]
countries = ["Indonesia", "USA", "India", "UK", "Germany"]
device_types = ["desktop", "mobile"]

users = []

for user_id in range(1, NUM_USERS + 1) :
    signup_date = fake.date_between(start_date='-90d', end_date='today')

    users.append({
        "user_id": user_id,
        "signup_date": signup_date,
        "country": random.choice(countries),
        "device_type": random.choice(device_types),
        "traffic_source": random.choice(traffic_sources),
        "plan_type": "free"
    })

df = pd.DataFrame(users)

df.to_csv("data/raw/users.csv", index=False)
print(f"Users generated: {len(df)}")