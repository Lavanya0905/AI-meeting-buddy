import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

# ---------------------------------------------------------
# LOAD CALENDARS (CHENNAI + GERMANY)
# ---------------------------------------------------------

def load_chennai_calendar():
    df = pd.read_csv("chennai_slots_large.csv")
    return df.to_dict(orient="records")


def load_germany_calendar():
    df = pd.read_csv("germany_slots_large.csv")
    return df.to_dict(orient="records")


# ---------------------------------------------------------
# PAST MEETINGS DATA (For fairness scoring)
# This can be a small CSV or mocked inline
# ---------------------------------------------------------

def load_past_meetings():
    """Mocked: each entry shows inconvenience to each team."""
    # Larger number = higher burden
    return {
        "india_burden": 12,
        "germany_burden": 19
    }


# ---------------------------------------------------------
# PARSE RAW SLOTS INTO DATETIME OBJECTS
# ---------------------------------------------------------

def parse_slots(data):
    slots = []
    for row in data:
        date = row['date']
        start = row['start']
        end = row['end']
        tz = ZoneInfo(row['timezone'])

        start_dt = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        end_dt = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

        if end_dt > start_dt:
            slots.append((start_dt, end_dt))

    return slots


# ---------------------------------------------------------
# FIND OVERLAPS BETWEEN 2 CALENDAR SETS
# ---------------------------------------------------------

def find_overlaps(raw_chennai, raw_germany):
    c_slots = parse_slots(raw_chennai)
    g_slots = parse_slots(raw_germany)

    overlaps = []
    for c_start, c_end in c_slots:
        for g_start, g_end in g_slots:

            latest_start = max(c_start, g_start)
            earliest_end = min(c_end, g_end)

            if latest_start < earliest_end:
                overlaps.append((latest_start, earliest_end))

    return overlaps


# ---------------------------------------------------------
# DETAILED SCORING SYSTEM (OPTION C)
# ---------------------------------------------------------

def score_slot(start_dt, end_dt, fairness_data):
    """Scores based on:
    - comfort working hours
    - slot length
    - preferred window alignment
    - day of week
    - fairness
    - recency
    - lunch time avoidance
    """

    ist = ZoneInfo("Asia/Kolkata")
    ger = ZoneInfo("Europe/Berlin")

    start_ist = start_dt.astimezone(ist)
    end_ist = end_dt.astimezone(ist)

    start_ger = start_dt.astimezone(ger)
    end_ger = end_dt.astimezone(ger)

    score = 0
    reasons = []

    # ---------------------------------------------------------
    # 1. Working Hours Comfort
    # ---------------------------------------------------------

    if 10 <= start_ist.hour < 17 and 9 <= start_ger.hour < 16:
        score += 15
        reasons.append("Ideal working hours for both teams")
    elif (10 <= start_ist.hour < 17) or (9 <= start_ger.hour < 16):
        score += 8
        reasons.append("Comfortable for one team")
    else:
        score -= 10
        reasons.append("Early/late meeting for one team")

    # ---------------------------------------------------------
    # 2. Slot Length
    # ---------------------------------------------------------

    duration = (end_dt - start_dt).seconds / 60  # minutes

    if duration >= 60:
        score += 10
        reasons.append("Full 1-hour meeting window")
    elif duration >= 45:
        score += 7
        reasons.append("Good 45-minute slot")
    elif duration >= 30:
        score += 4
        reasons.append("Minimum acceptable slot length")
    else:
        score -= 5
        reasons.append("Too short slot")

    # ---------------------------------------------------------
    # 3. Preferred Window
    # ---------------------------------------------------------

    if (11 <= start_ist.hour < 16) and (10 <= start_ger.hour < 15):
        score += 12
        reasons.append("Inside preferred meeting window")
    elif (11 <= start_ist.hour < 16) or (10 <= start_ger.hour < 15):
        score += 7
        reasons.append("Partial preference match")
    else:
        score -= 8
        reasons.append("Outside preference window")

    # ---------------------------------------------------------
    # 4. Day of Week
    # ---------------------------------------------------------

    dow = start_ist.weekday()
    if dow in [1, 2, 3]:
        score += 5
        reasons.append("Mid-week meetings preferred")
    elif dow == 0:
        score += 2
        reasons.append("Monday acceptable")
    elif dow == 4:
        score += 0
    else:
        score -= 20
        reasons.append("Weekend is not recommended")

    # ---------------------------------------------------------
    # 5. Fairness Compensation
    # ---------------------------------------------------------

    india = fairness_data["india_burden"]
    germany = fairness_data["germany_burden"]

    if germany > india:  # Germany suffered more
        if 10 <= start_ger.hour < 15:
            score += 20
            reasons.append("Balances past inconvenience for Germany")

    elif india > germany:
        if 11 <= start_ist.hour < 16:
            score += 20
            reasons.append("Balances past inconvenience for India")
    else:
        score += 0

    # ---------------------------------------------------------
    # 6. Recency
    # ---------------------------------------------------------

    days_ahead = (start_dt.date() - datetime.now().date()).days

    if days_ahead <= 3:
        score += 6
        reasons.append("Soonest available slot")
    elif days_ahead <= 7:
        score += 4
    elif days_ahead <= 14:
        score += 2
    else:
        score += 1

    # ---------------------------------------------------------
    # 7. Lunch Time Avoidance
    # ---------------------------------------------------------

    if not (13 <= start_ist.hour < 14):
        score += 3
        reasons.append("Avoids lunch hour")

    return score, reasons
