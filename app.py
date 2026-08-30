import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Deep Reader Agent",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Deep Reader Agent")
st.caption("Autonomous Scout & Density Reader — NFL Intelligence Pillar")

# Retrieve API key from Streamlit Secrets or Environment
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please configure it in Streamlit Secrets.")
    st.stop()

# --- Search Vectors UI ---
st.subheader("Tactical Search Vectors")

default_focus = "Bobby Slowik offensive scheme, Next Gen Stats, Cover 6 match, NFL EPA/play, All-22 film study, simulated pressures, 2026 NFL scheme breakdowns"
focus_keywords = st.text_area(
    "Focus Keywords & Core Concepts (What to scout for):",
    value=default_focus,
    help="Add your favorite coaches, schemes, metrics, or tactical concepts here."
)

default_exclude = "fantasy football, waiver wire, betting odds, injury reports, generic press conference quotes, mock draft, articles published before 2026"
exclude_keywords = st.text_area(
    "Exclusions & Noise Filters (What to eliminate):",
    value=default_exclude,
    help="Forces Gemini to drop surface-level sports chatter and outdated archives."
)

st.divider()

# --- Scout Execution ---
if st.button("⚡ Scout High-Density Content", type="primary"):
    with st.spinner("Scouting live web for 2026 tactical breakdowns & scoring density..."):
        # Stable endpoint: gemini-3.6-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt = f"""
You are an elite NFL tactical analyst and content curation agent.
Search the live web strictly for deep, technical NFL analytics articles, Substacks, and film breakdowns published in the current year (2026).

SEARCH PRIORITIES:
{focus_keywords}

STRICT EXCLUSIONS & FILTERS:
{exclude_keywords}
- STRICT DATE CONSTRAINT: DO NOT return any articles published in 2025, 2024, or earlier. Every result MUST be from 2026.

TASK & OUTPUT RULES:
1. Scout and select 4-5 high-density articles/breakdowns published in 2026 that match the priorities.
2. For each article, format as:
   - ### Article Title
   - **Source & Date**: Author / Publication Source | Date Published (Must be 2026) | [Read Full Piece](Direct URL)
   - **Information Density Score**: Score from 1.0 to 10.0 (based strictly on depth of scheme/metrics vs surface recap)
   - **Key Tactical Takeaways**: 3 concise bullet points breaking down the specific scheme, coverage, play concept, or metric mechanics.
   - **Strategic Impact**: 1 sentence on the broader takeaway for modern NFL systems.

Ensure every piece is strictly from 2026 and formatted cleanly for mobile reading.
"""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "tools": [{"google_search": {}}]
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                st.markdown(text)
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Execution Error: {e}")
