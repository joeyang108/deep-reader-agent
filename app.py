import streamlit as st
from google import genai
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

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

st.divider()
st.subheader("System Status")
st.write("UI Scaffolding: **Active**")
st.write("Target Pillars: **NFL Analytics | Soccer Systems | Sonic Architecture**")

# Interactive verification ping
if st.button("Ping Gemini 2.5 Flash", type="primary"):
    with st.spinner("Connecting to Google AI Studio..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="State in 2 crisp sentences that the Deep Reader Agent intelligence pipeline is initialized and ready for tactical feed ingestion."
            )
            st.success("API Connection Verified!")
            st.info(response.text)
        except Exception as e:
            st.error(f"Connection Error: {e}")
