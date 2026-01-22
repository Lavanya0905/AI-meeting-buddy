import streamlit as st
from meeting_agent import meeting_agent, generate_ics

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Meeting Buddy – Smart Scheduler",
    page_icon="🤖",
    layout="centered"
)

# ---------------------------------------------------------
# SIMPLE STYLES FOR CARDS
# ---------------------------------------------------------

card_style = """
<style>
.card {
    background-color: #f1f3f4;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}
.slot-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 6px;
}
.time-text {
    font-size: 16px;
    margin-top: 4px;
}
</style>
"""
st.markdown(card_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🤝 AI Meeting Buddy – Smart Scheduler")
st.write(
    """
This AI Meeting Buddy suggests the **Top 2 common meeting slots** between  
🇮🇳 **Chennai (IST)** and 🇩🇪 **Germany (local time)**,  
and lets you **download calendar invites (.ics)** for each slot.
"""
)

st.markdown("---")

# ---------------------------------------------------------
# MAIN BUTTON
# ---------------------------------------------------------

if st.button("🔍 Find Top 2 Meeting Slots"):
    data = meeting_agent()

    if not data["results"]:
        st.error("No common free slots found. Please check the calendar data.")
    else:
        st.success(data["message"])

        # Loop through Top 2 slots
        for idx, slot in enumerate(data["results"], start=1):
            # Card container
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # Title
            st.markdown(
                f"<div class='slot-title'>#{idx} Suggested Slot</div>",
                unsafe_allow_html=True
            )

            # Times in both zones
            st.markdown(
                f"<div class='time-text'>🇮🇳 <b>IST:</b> {slot['ist_time']}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='time-text'>🇩🇪 <b>Germany:</b> {slot['germany_time']}</div>",
                unsafe_allow_html=True
            )

            # Generate ICS content for this slot
            ics_content = generate_ics(slot["start_dt"], slot["end_dt"], title="Vendor–Distributor Meeting")

            # Download button
            st.download_button(
                label="📅 Download Meeting Invite (.ics)",
                data=ics_content,
                file_name=f"meeting_slot_{idx}.ics",
                mime="text/calendar",
                key=f"download_ics_{idx}"
            )

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Click the button above to generate AI-recommended meeting slots.")

st.markdown("---")
st.caption("AI Meeting Buddy – Phase 1: Smart Scheduling with downloadable calendar invites.")
