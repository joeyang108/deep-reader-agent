import streamlit as st
import google.generativeai as genai
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

# Configure Gemini Client
genai.configure(api_key=api_key)

st.divider()
st.subheader("System Status")
st.write("UI Scaffolding: **Active**")
st.write("Target Pillars: **NFL Analytics | Soccer Systems | Sonic Architecture**")

# Interactive verification ping
if st.button("Ping Gemini 2.5 Flash", type="primary"):
    with st.spinner("Connecting to Google AI Studio..."):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                "State in 2 crisp sentences that the Deep Reader Agent intelligence pipeline is initialized and ready for tactical feed ingestion."
            )
            st.success("API Connection Verified!")
            st.info(response.text)
        except Exception as e:
            st.error(f"Connection Error: {e}")
