import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Deep Reader Agent",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Deep Reader Agent")
st.caption("Personal Intelligence Terminal - Phase 1 Verification")

# Retrieve API key from Streamlit Secrets or Environment
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please configure it in Streamlit Secrets.")
    st.stop()

st.divider()
st.subheader("System Status")
st.write("UI Scaffolding: **Active**")
st.write("Target Pillars: **NFL Analytics | Soccer Systems | Sonic Architecture**")

# Interactive verification ping
if st.button("Ping Gemini 2.5 Flash", type="primary"):
    with st.spinner("Connecting directly to Google AI Studio REST API..."):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": "State in 2 crisp sentences that the Deep Reader Agent intelligence pipeline is initialized and ready for tactical feed ingestion."
                }]
            }]
        }
        
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                st.success("API Connection Verified!")
                st.info(text)
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Network Error: {e}")
