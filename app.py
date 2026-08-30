import streamlit as st
import requests
import re
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

default_focus = "Ben Slovak articles, Bill Barnwell articles, Next Gen Stats, Cover 6 match, NFL EPA/play, All-22 film study, simulated pressures, 2026 NFL scheme breakdowns"
focus_keywords = st.text_area(
    "Focus Keywords & Byline Targets (What to scout for):",
    value=default_focus,
    help="Target specific writers, coaches, schemes, or metrics."
)

default_exclude = "fantasy football, waiver wire, betting odds, injury reports, generic press conference quotes, mock draft, articles published before 2026"
exclude_keywords = st.text_area(
    "Exclusions & Noise Filters (What to eliminate):",
    value=default_exclude,
    help="Drops surface chatter and outdated archives."
)

st.divider()

# --- Scout Execution ---
if st.button("⚡ Scout High-Density Content", type="primary"):
    with st.spinner("Scouting 2026 technical breakdowns with verified inline sources..."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt = f"""
You are an elite NFL tactical analyst and curation agent.
Search the live web strictly for deep, technical NFL analytics articles, Substacks, and film breakdowns published in 2026.

SEARCH PRIORITIES:
{focus_keywords}

STRICT EXCLUSIONS & FILTERS:
{exclude_keywords}
- STRICT DATE CONSTRAINT: Every breakdown must be from 2026.

STRUCTURE & FORMATTING RULES:
Output 4 to 5 distinct article cards separated by "---".
For every single article, follow this exact structure:

### [Number]. [Article / Concept Title]
- **Author / Source & Date**: [Author/Publication] | 2026
- **Information Density Score**: [Score]/10
- **Key Tactical Takeaways**:
  * [Takeaway 1]
  * [Takeaway 2]
  * [Takeaway 3]
- **Strategic Impact**: [1 macro sentence]
- **Source Link**: [Insert the exact live webpage URL found in Google Search]
---
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
                candidate = data.get("candidates", [{}])[0]
                raw_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")

                # Split output into individual article cards
                sections = raw_text.split("---")

                for section in sections:
                    cleaned_section = section.strip()
                    if not cleaned_section:
                        continue

                    # Extract the Source Link URL if present
                    url_match = re.search(r"\*\*Source Link\*\*:\s*\[?(https?://[^\s\]\)\>]+)\]?", cleaned_section)
                    
                    # Remove the raw link line so we render a clean button instead
                    display_text = re.sub(r"-\s*\*\*Source Link\*\*:\s*.*", "", cleaned_section).strip()

                    # Render card content
                    st.markdown(display_text)

                    # Render direct inline button
                    if url_match:
                        target_url = url_match.group(1).rstrip(".")
                        st.link_button("🔗 Open Full Piece & Film Breakdown", target_url)

                    st.divider()

            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Execution Error: {e}")
