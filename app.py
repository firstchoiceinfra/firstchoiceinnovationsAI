import streamlit as st
import google.generativeai as genai
import uuid, re, json, os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from duckduckgo_search import DDGS

# UI Settings
st.set_page_config(page_title="J.A.R.V.I.S. Pro", page_icon="⚡", layout="wide")

# API Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Memory Management
MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    return {}

# UI & Sidebar
if "history" not in st.session_state: st.session_state.history = load_memory()
if "current_id" not in st.session_state: st.session_state.current_id = str(uuid.uuid4())

with st.sidebar:
    st.title("⚡ J.A.R.V.I.S. Pro")
    if st.button("➕ नई चैट", use_container_width=True):
        st.session_state.current_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    st.subheader("📜 पिछली बातें (History)")
    for cid, data in list(st.session_state.history.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(data.get("title", "नया विषय"), key=cid):
            st.session_state.current_id = cid
            st.rerun()
        if col2.button("🗑️", key=f"del_{cid}"):
            del st.session_state.history[cid]
            save_memory(st.session_state.history)
            st.rerun()

# Model Initialization
model = genai.GenerativeModel('gemini-1.5-pro')

# Main Chat Logic
if st.session_state.current_id not in st.session_state.history:
    st.session_state.history[st.session_state.current_id] = {"title": "नया विषय", "messages": []}

chat_data = st.session_state.history[st.session_state.current_id]

st.title("नमस्कार, Jitendra! चलिए शुरू करें")

# Display History
for msg in chat_data["messages"]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Input Handling
if prompt := st.chat_input("Gemini से कहें..."):
    # Title Setting
    if len(chat_data["messages"]) == 0:
        chat_data["title"] = prompt[:25]
    
    chat_data["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("⚡ J.A.R.V.I.S. सोच रहा है..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            chat_data["messages"].append({"role": "assistant", "content": response.text})
            save_memory(st.session_state.history)
            
            # Voice Reply
            tts = gTTS(text="कोड तैयार है बॉस", lang='hi')
            tts.save("r.mp3")
            st.audio("r.mp3", autoplay=True)
