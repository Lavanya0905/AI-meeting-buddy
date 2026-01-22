import pandas as pd
from datetime import datetime, timedelta

# Settings
num_days = 90  # Approx 3 months
start_date = datetime(2025, 1, 1)

# Daily free working slots (Realistic Pattern)
slots = [
    ("09:00", "10:30"),
    ("11:00", "12:30"),
    ("13:00", "14:00"),
    ("14:30", "15:30"),
    ("16:00", "17:00"),
    ("17:30", "18:30"),
]

def generate_slots(timezone, filename):
    data = []

    for d in range(num_days):
        date = (start_date + timedelta(days=d)).strftime("%Y-%m-%d")
        for start, end in slots:
            data.append([date, start, end, timezone])

    df = pd.DataFrame(data, columns=["date", "start", "end", "timezone"])
    df.to_csv(filename, index=False)
    print(f"Generated: {filename} with {len(df)} rows")

# Generate datasets
generate_slots("Asia/Kolkata", "chennai_slots_large.csv")
generate_slots("Europe/Berlin", "germany_slots_large.csv")
