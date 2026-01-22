from mcp_tools import (
    load_chennai_calendar,
    load_germany_calendar,
    load_past_meetings,
    find_overlaps,
    score_slot
)
from zoneinfo import ZoneInfo

def format_time(start_dt, end_dt):
    ist = ZoneInfo("Asia/Kolkata")
    ger = ZoneInfo("Europe/Berlin")

    return {
        "ist_time": f"{start_dt.astimezone(ist).strftime('%Y-%m-%d %H:%M')} → {end_dt.astimezone(ist).strftime('%H:%M')}",
        "germany_time": f"{start_dt.astimezone(ger).strftime('%Y-%m-%d %H:%M')} → {end_dt.astimezone(ger).strftime('%H:%M')}"
    }


def meeting_agent():

    # Load data
    raw_chennai = load_chennai_calendar()
    raw_germany = load_germany_calendar()
    fairness_data = load_past_meetings()

    # Find overlaps
    overlaps = find_overlaps(raw_chennai, raw_germany)
    if not overlaps:
        return {"message": "❌ No common free slots", "results": []}

    # Score all slots
    slot_ranking = []
    for start_dt, end_dt in overlaps:
        score, _ = score_slot(start_dt, end_dt, fairness_data)
        slot_ranking.append((score, start_dt, end_dt))

    # Sort by score
    slot_ranking.sort(reverse=True, key=lambda x: x[0])

    # Pick TOP 2 slots
    top_2 = slot_ranking[:2]

    # Convert formatting for UI
    results = []
    for _, s, e in top_2:
        slot_info = format_time(s, e)
        slot_info["start_dt"] = s
        slot_info["end_dt"] = e
        results.append(slot_info)


    return {
        "message": "Top 2 Suggested Meeting Slots",
        "results": results
    }
def generate_ics(start_dt, end_dt, title="Vendor–Distributor Meeting"):
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
END:VEVENT
END:VCALENDAR
"""
    return ics_content



if __name__ == "__main__":
    print(meeting_agent())
