import streamlit as st
import google.generativeai as genai
import uuid, re, json, os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr

# 1. UI Settings
st.set_page_config(page_title="J.A.R.V.I.S. Pro", page_icon="⚡", layout="wide")

# 2. API Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key missing!")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Memory Management
MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f)

# 4. Sidebar History (Gemini Style)
if "history" not in st.session_state: st.session_state.history = load_memory()
if "current_id" not in st.session_state: st.session_state.current_id = str(uuid.uuid4())

with st.sidebar:
    st.title("⚡ J.A.R.V.I.S.")
    if st.button("➕ नई चैट", use_container_width=True):
        st.session_state.current_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    st.subheader("📜 हाल ही के (Recent)")
    for cid, data in list(st.session_state.history.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(data.get("title", "नया विषय"), key=cid):
            st.session_state.current_id = cid
            st.rerun()
        if col2.button("🗑️", key=f"del_{cid}"):
            del st.session_state.history[cid]
            save_memory(st.session_state.history)
            st.rerun()

# 5. Model Initialization
model = genai.GenerativeModel('gemini-1.5-pro')

if st.session_state.current_id not in st.session_state.history:
    st.session_state.history[st.session_state.current_id] = {"title": "नया विषय", "messages": []}

chat_data = st.session_state.history[st.session_state.current_id]

st.title("नमस्ते, Jitendra! चलिए शुरू करें")

# 6. Display Chat History
for msg in chat_data["messages"]:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# ==========================================
# 7. BOTTOM CONTROLS (Gemini UI Replica)
# ==========================================

# टाइपिंग बार के ठीक ऊपर '+' और 'Mic' को सेट करना
col1, col2 = st.columns([0.15, 0.85])

uploaded_file = None
with col1:
    # ➕ बटन (Popover) - इस पर क्लिक करते ही अपलोड का ऑप्शन खुलेगा
    with st.popover("➕", help="इमेज या फ़ाइल अपलोड करें"):
        uploaded_file = st.file_uploader("🖼️ फोटो अपलोड करें", type=['png', 'jpg', 'jpeg'])

with col2:
    # 🎤 माइक बटन 
    audio_bytes = audio_recorder(text="🎤 बोलें...", recording_color="#e84118", neutral_color="#4cd137")

# टाइपिंग एरिया
prompt = st.chat_input("Gemini से कहें...")

# ==========================================
# 8. MULTILINGUAL VOICE PROCESSING 
# ==========================================
voice_prompt = None
if audio_bytes:
    with st.spinner("सुन रहा हूँ..."):
        with open("temp.wav", "wb") as f: f.write(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile("temp.wav") as source:
            try:
                # 'hi-IN' सेट करने से यह हिंदी, इंग्लिश और मराठी तीनों को अच्छे से समझ लेता है
                raw_text = r.recognize_google(r.record(source), language="hi-IN")
                voice_prompt = raw_text
                # स्क्रीन पर तुरंत दिखाना
                st.success(f"🗣️ आपने कहा: {voice_prompt}") 
            except:
                st.error("आवाज़ साफ़ नहीं आई, कृपया दोबारा बोलें।")

# टाइपिंग या वॉइस दोनों में से जो भी हो, उसे फाइनल कमांड मान लें
final_prompt = prompt if prompt else voice_prompt

# ==========================================
# 9. AI RESPONSE GENERATION
# ==========================================
if final_prompt:
    # चैट का नाम ऑटोमैटिक सेट करना
    if len(chat_data["messages"]) == 0:
        chat_data["title"] = final_prompt[:25]
    
    chat_data["messages"].append({"role": "user", "content": final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("⚡ J.A.R.V.I.S. सोच रहा है..."):
            if uploaded_file:
                # अगर फोटो अपलोड की है तो विज़न मॉडल यूज़ होगा
                img = Image.open(uploaded_file)
                response = model.generate_content([final_prompt, img])
            else:
                # नॉर्मल चैट
                history_format = [{"role": m["role"], "parts": [m["content"]]} for m in chat_data["messages"][:-1]]
                chat_session = model.start_chat(history=history_format)
                response = chat_session.send_message(final_prompt)
            
            st.markdown(response.text)
            chat_data["messages"].append({"role": "assistant", "content": response.text})
            save_memory(st.session_state.history)
