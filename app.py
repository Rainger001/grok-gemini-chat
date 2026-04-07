import streamlit as st
import os
import requests
import google.generativeai as genai
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Grok + Gemini Chat", layout="wide")
st.title("🤖 Grok + Gemini Multi-AI Chat")
st.markdown("One prompt → Both respond → Best combined answer")

grok_key = st.secrets.get("GROK_API_KEY")
gemini_key = st.secrets.get("GEMINI_API_KEY")

if not grok_key or not gemini_key:
    st.error("❌ API keys not configured. Please add them in Streamlit secrets.")
    st.stop()

genai.configure(api_key=gemini_key)

def call_grok(prompt):
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}
        data = {"model": "grok-4.1-fast", "messages": [{"role": "user", "content": prompt}]}
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        return resp.json()["choices"][0]["message"]["content"] if resp.ok else "Grok error"
    except:
        return "Grok connection error"

def call_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model.generate_content(prompt).text
    except:
        return "Gemini error"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask anything...")
if prompt:
    with st.spinner("Calling Grok & Gemini..."):
        grok_resp = call_grok(prompt)
        gemini_resp = call_gemini(prompt)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Grok")
        st.markdown(grok_resp)
    with col2:
        st.subheader("🔵 Gemini")
        st.markdown(gemini_resp)

    with st.spinner("Creating best combined answer..."):
        best_answer = call_gemini(f"Combine these two responses into one clear, accurate, and useful answer.\n\nGrok: {grok_resp}\n\nGemini: {gemini_resp}")

    st.subheader("🏆 Best Combined Answer")
    st.markdown(best_answer)

    pd.DataFrame([{
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "grok": grok_resp,
        "gemini": gemini_resp,
        "best_answer": best_answer
    }]).to_csv("multi_ai_chat_db.csv", mode='a', header=not os.path.exists("multi_ai_chat_db.csv"), index=False)

    st.session_state.messages.append({"role": "assistant", "content": best_answer})
