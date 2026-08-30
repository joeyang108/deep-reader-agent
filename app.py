import streamlit as st
import requests
import json
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

OUTPUT INSTRUCTIONS:
Return a JSON array containing 4-5 high-density article cards.
Each JSON object must have the following keys:
- "title": (string) Title of the technical breakdown or article.
- "source_name": (string) Author or Publication Name (2026).
- "source_url": (string) The exact verified URL found via Google Search for this piece.
- "density_score": (string or float) Information Density Score (e.g. 8.9/10).
- "takeaways": (list of strings) 3 concise bullet points detailing specific scheme mechanics, coverage match rules, or metrics.
- "strategic_impact": (string) 1 sentence on the broader takeaway for modern NFL systems.

Output ONLY valid JSON.
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
                text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Extract grounding chunks as a fallback map
                grounding_metadata = candidate.get("groundingMetadata", {})
                chunks = grounding_metadata.get("groundingChunks", [])
                fallback_urls = [c.get("web", {}).get("uri") for c in chunks if c.get("web", {}).get("uri")]

                # Clean markdown backticks if model wrapped JSON
                cleaned_text = text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                try:
                    articles = json.loads(cleaned_text)
                    for i, item in enumerate(articles):
                        title = item.get("title", f"Tactical Breakdown {i+1}")
                        source_name = item.get("source_name", "Analytics Source (2026)")
                        
                        # Match verified URL or fallback to grounding chunk index
                        source_url = item.get("source_url")
                        if not source_url or "http" not in source_url:
                            if i < len(fallback_urls):
                                source_url = fallback_urls[i]
                            elif fallback_urls:
                                source_url = fallback_urls[0]

                        density = item.get("density_score", "8.5/10")
                        takeaways = item.get("takeaways", [])
                        strategic_impact = item.get("strategic_impact", "")

                        # Render each article card strictly inline
                        st.subheader(f"{i+1}. {title}")
                        st.caption(f"**Author / Source**: {source_name} | **Density Score**: {density}")
                        
                        st.markdown("**Key Tactical Takeaways:**")
                        for bullet in takeaways:
                            st.markdown(f"- {bullet}")
                            
                        if strategic_impact:
                            st.markdown(f"**Strategic Impact:** {strategic_impact}")
                            
                        if source_url:
                            st.link_button(f"🔗 Read Full Piece on {source_name.split('|')[0].strip()}", source_url)
                        
                        st.divider()

                except Exception:
                    # Direct markdown fallback if JSON parsing fails
                    st.markdown(text)
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Execution Error: {e}")
