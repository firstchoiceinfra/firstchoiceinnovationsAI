import streamlit as st
import google.generativeai as genai
import uuid
import re
import json
import os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from duckduckgo_search import DDGS

# 1. Page Config
st.set_page_config(page_title="Firstchoice J.A.R.V.I.S.", page_icon="⚡", layout="wide")

# 2. Memory System
MEMORY_FILE = "firstchoice_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f)

# 3. Sidebar (History Manager)
with st.sidebar:
    st.title("⚡ J.A.R.V.I.S. OMNI")
    if st.button("➕ नया प्रोजेक्ट शुरू करें", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        save_memory(st.session_state.history_list)
        st.rerun()

    st.divider()
    st.subheader("📜 पुरानी चैट्स (History)")
    
    if "history_list" not in st.session_state:
        st.session_state.history_list = load_memory()
    
    # पुरानी चैट्स को लिस्ट करना
    for chat_id, messages in list(st.session_state.history_list.items()):
        # चैट का नाम (पहली लाइन से)
        chat_name = messages[0]["content"][:20] + "..." if messages else "नया चैट"
        
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(f"{chat_name}", key=f"btn_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.rerun()
        if col2.button("🗑️", key=f"del_{chat_id}"):
            del st.session_state.history_list[chat_id]
            save_memory(st.session_state.history_list)
            # अगर करंट चैट डिलीट हुई, तो नई चैट बनाओ
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = str(uuid.uuid4())
                st.session_state.history_list[st.session_state.current_chat_id] = []
            st.rerun()

# 4. State Initializer
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.history_list:
    st.session_state.current_chat_id = list(st.session_state.history_list.keys())[0] if st.session_state.history_list else str(uuid.uuid4())
    if st.session_state.current_chat_id not in st.session_state.history_list:
        st.session_state.history_list[st.session_state.current_chat_id] = []
        save_memory(st.session_state.history_list)

# 5. Model Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
SYSTEM_PROMPT = "तुम J.A.R.V.I.S. हो, Sonnet 5 जैसा दिमाग है। <thinking> में प्लान बनाओ, फिर कोड दो।"
try:
    model = genai.GenerativeModel('gemini-3.6-flash', system_instruction=SYSTEM_PROMPT)
except:
    model = genai.GenerativeModel('gemini-pro', system_instruction=SYSTEM_PROMPT)

# 6. Main UI
st.title("J.A.R.V.I.S. Omni Intelligence ⚡")
st.markdown("**🦻 'Hello FC' बोलकर धीरे से कमांड दें।**")

# Chat Display
current_messages = st.session_state.history_list[st.session_state.current_chat_id]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Logic
prompt = st.chat_input("कमांड दें...")

# Voice Processing (Whisper Mode)
audio_bytes = audio_recorder(text="क्लिक करें...", icon_size="2x")
if audio_bytes:
    with open("temp.wav", "wb") as f: f.write(audio_bytes)
    r = sr.Recognizer()
    r.energy_threshold = 100 # बहुत धीमी आवाज़ भी सुनेगा
    with sr.AudioFile("temp.wav") as source:
        try:
            raw = r.recognize_google(r.record(source), language="hi-IN").lower()
            if any(w in raw for w in ["hello fc", "हेलो एफसी", "hello f c", "हेलो ऐप"]):
                prompt = raw
                st.success("✅ सुना गया!")
            else: st.warning("⚠️ कमांड नहीं सुनी गई, 'Hello FC' बोलें।")
        except: st.error("आवाज़ बहुत धीमी है।")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("⚡ J.A.R.V.I.S. Architecting..."):
            response = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]).send_message(prompt)
            st.markdown(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
            save_memory(st.session_state.history_list)
            # Voice Reply
            tts = gTTS(text="कोड तैयार है बॉस", lang='hi')
            tts.save("r.mp3")
            st.audio("r.mp3", autoplay=True)
