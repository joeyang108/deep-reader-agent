import streamlit as st
import requests
import time
import os

st.set_page_config(
    page_title="Deep Reader Agent",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Deep Reader Agent")
st.caption("Autonomous Scout & Density Reader — NFL Pillar")

# Retrieve API key from Streamlit Secrets or Environment
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please configure it in Streamlit Secrets.")
    st.stop()

# --- Search Vectors UI ---
st.subheader("Tactical Search Vectors")

default_focus = "Bobby Slowik, Next Gen Stats, NFL EPA, All-22 film study, NFL Deep Analysis"
focus_keywords = st.text_area(
    "Focus Keywords & Core Concepts (What to scout for):",
    value=default_focus,
    help="Add your favorite coaches, schemes, metrics, or tactical concepts here."
)

default_exclude = "fantasy football, waiver wire, betting odds, injury reports, generic press conference quotes, mock draft"
exclude_keywords = st.text_area(
    "Exclusions & Noise Filters (What to eliminate):",
    value=default_exclude,
    help="Forces Gemini to drop surface-level sports chatter."
)

st.divider()

# --- Scout Execution with Auto-Retry Logic ---
if st.button("⚡ Scout High-Density Content", type="primary"):
    with st.spinner("Scouting live web, discovering independent feeds, and scoring density..."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt = f"""
You are an elite NFL tactical analyst and content curation agent.
Search the live web for deep, technical NFL analytics articles, Substacks, and film breakdowns published recently.

SEARCH PRIORITIES:
{focus_keywords}

STRICT EXCLUSIONS (DO NOT RETURN ARTICLES ABOUT THESE):
{exclude_keywords}

TASK & OUTPUT RULES:
1. Scout and select the 4-5 highest density articles/breakdowns found on the live web matching the priorities.
2. For each article, provide:
   - Article Title (as a Markdown header)
   - Author / Publication Source & Direct Markdown Link (e.g. [Read Full Piece](URL))
   - Information Density Score: Score from 1.0 to 10.0 (based strictly on depth of scheme/metrics vs surface recap)
   - Key Tactical Takeaways: 3 concise bullet points breaking down the specific scheme, coverage, play concept, or metric mechanics.
   - Why It Matters: 1 sentence on the strategic takeaway.

Ensure the output is clean, readable, and formatted for a mobile reading screen.
"""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "tools": [{"google_search": {}}]
        }

        # Handle rate limits gracefully with backoff
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(text)
                    success = True
                    break
                elif res.status_code == 429:
                    wait_time = (attempt + 1) * 4
                    st.warning(f"Quota burst limit reached. Retrying automatically in {wait_time}s (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    st.error(f"API Error ({res.status_code}): {res.text}")
                    break
            except Exception as e:
                st.error(f"Execution Error: {e}")
                break
        
        if not success and res.status_code == 429:
            st.error("Rate limit saturated. Please wait 30 seconds before triggering another scout, or link billing in Google AI Studio to lift tier caps.")
