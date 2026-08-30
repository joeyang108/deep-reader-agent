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

default_focus = "Ben Solak articles, Bill Barnwell articles, Next Gen Stats, Cover 6 match, NFL EPA/play, All-22 film study, simulated pressures, 2026 NFL scheme breakdowns"
focus_keywords = st.text_area(
    "Focus Keywords & Byline Targets (What to scout for):",
    value=default_focus,
    help="Target specific writers, coaches, schemes, or metrics."
)

default_exclude = "youtube.com, youtu.be, podcasts, audio recordings, video clips, video highlights, fantasy football, waiver wire, betting odds, injury reports, generic press conference quotes, mock draft, articles published before 2026"
exclude_keywords = st.text_area(
    "Exclusions & Noise Filters (What to eliminate):",
    value=default_exclude,
    help="Forces exclusion of video/audio media and non-technical chatter."
)

st.divider()

# --- Scout Execution ---
if st.button("⚡ Scout High-Density Content", type="primary"):
    with st.spinner("Scouting 2026 written breakdowns with exact publication dates & full URLs..."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        prompt = f"""
You are an elite NFL tactical analyst and curation agent.
Search the live web strictly for long-form WRITTEN NFL analytics articles, Substacks, and written film breakdowns published in 2026.

SEARCH PRIORITIES:
{focus_keywords}

STRICT EXCLUSIONS & FILTERS:
{exclude_keywords}
- STRICT MEDIA CONSTRAINT: Search ONLY for written text articles/Substacks. DO NOT include YouTube links, video feeds, podcasts, or audio content.
- STRICT DATE CONSTRAINT: Every scouted piece must be from 2026 with an exact publication date (e.g., "August 25, 2026").

STRUCTURE & FORMATTING RULES:
Output 4 to 5 distinct written article cards separated by "---".
DO NOT invent or guess URLs in your text.
For every single article, follow this exact structure:

### [Number]. [Article / Concept Title]
- **Author / Source**: [Author Name / Publication Name]
- **Exact Publication Date**: [Month Day, Year — e.g. August 25, 2026]
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
                
                # Filter out video/multimedia URLs from chunks
                valid_chunks = []
                for c in chunks:
                    uri = c.get("web", {}).get("uri", "")
                    if uri and not any(bad in uri.lower() for bad in ["youtube.com", "youtu.be", "podcast", "spotify.com", "apple.com/podcast"]):
                        valid_chunks.append(c)

                # Split text into article cards
                sections = [s.strip() for s in raw_text.split("---") if s.strip()]
                
                current_cursor = 0
                for i, section in enumerate(sections):
                    st.markdown(section)
                    
                    card_start = raw_text.find(section, current_cursor)
                    card_end = card_start + len(section)
                    current_cursor = card_end
                    
                    matched_uri = None
                    
                    # Match exact segment to valid grounding chunks
                    for sup in supports:
                        seg = sup.get("segment", {})
                        seg_start = seg.get("startIndex", 0)
                        indices = sup.get("groundingChunkIndices", [])
                        
                        if card_start <= seg_start <= card_end and indices:
                            for idx in indices:
                                if idx < len(chunks):
                                    candidate_uri = chunks[idx].get("web", {}).get("uri", "")
                                    if candidate_uri and not any(bad in candidate_uri.lower() for bad in ["youtube.com", "youtu.be", "podcast"]):
                                        matched_uri = candidate_uri
                                        break
                            if matched_uri:
                                break
                    
                    # Fallback to valid chunk index
                    if not matched_uri and i < len(valid_chunks):
                        matched_uri = valid_chunks[i].get("web", {}).get("uri")

                    # Display the full unabbreviated URL in code format + clickable link
                    if matched_uri:
                        st.markdown(f"**Full URL:** `{matched_uri}`")
                        st.link_button("🔗 Open Full Written Piece", matched_uri)
                        
                    st.divider()

            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Execution Error: {e}")
