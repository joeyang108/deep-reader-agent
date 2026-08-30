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
DO NOT invent or write any URLs in your text.
For every single article, follow this exact structure:

### [Number]. [Article / Concept Title]
- **Author / Source & Date**: [Author/Publication] | 2026
- **Information Density Score**: [Score]/10
- **Key Tactical Takeaways**:
  * [Takeaway 1]
  * [Takeaway 2]
  * [Takeaway 3]
- **Strategic Impact**: [1 macro sentence]
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
                
                # Extract verified Google Grounding Chunks and Support Mappings
                grounding_metadata = candidate.get("groundingMetadata", {})
                chunks = grounding_metadata.get("groundingChunks", [])
                supports = grounding_metadata.get("groundingSupports", [])
                
                # Split text into article cards
                sections = [s.strip() for s in raw_text.split("---") if s.strip()]
                
                # Build character index spans for each card
                current_cursor = 0
                for i, section in enumerate(sections):
                    st.markdown(section)
                    
                    card_start = raw_text.find(section, current_cursor)
                    card_end = card_start + len(section)
                    current_cursor = card_end
                    
                    # Find ground-truth URI tied to this specific section
                    matched_uri = None
                    matched_title = None
                    
                    for sup in supports:
                        seg = sup.get("segment", {})
                        seg_start = seg.get("startIndex", 0)
                        indices = sup.get("groundingChunkIndices", [])
                        
                        if card_start <= seg_start <= card_end and indices:
                            chunk_idx = indices[0]
                            if chunk_idx < len(chunks):
                                web_data = chunks[chunk_idx].get("web", {})
                                matched_uri = web_data.get("uri")
                                matched_title = web_data.get("title", "Original Article")
                                break
                    
                    # Fallback to index matching if segment offset not strictly found
                    if not matched_uri and i < len(chunks):
                        web_data = chunks[i].get("web", {})
                        matched_uri = web_data.get("uri")
                        matched_title = web_data.get("title", "Original Article")

                    # Render native verified button
                    if matched_uri:
                        st.link_button(f"🔗 Read Source ({matched_title[:45]}...)", matched_uri)
                        
                    st.divider()

            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Execution Error: {e}")
