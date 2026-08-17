import streamlit as st
import google.generativeai as genai
import uuid
import re
import json
import os
import pandas as pd
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from duckduckgo_search import DDGS
from fpdf import FPDF

# 1. Page Config
st.set_page_config(page_title="Firstchoice HQ", page_icon="🏢", layout="wide")

# 2. 🔒 SECURITY SYSTEM (मास्टर पासवर्ड)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Firstchoice Security Protocol")
    st.markdown("सिस्टम एक्सेस करने के लिए मास्टर पासवर्ड दर्ज करें।")
    pwd = st.text_input("Password", type="password")
    if st.button("Unlock J.A.R.V.I.S."):
        if pwd == "FC2026":  # आप इसे बाद में बदल सकते हैं
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Access Denied!")
    st.stop() # जब तक पासवर्ड नहीं डलेगा, ऐप आगे नहीं बढ़ेगा

# 3. API & Memory Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

MEMORY_FILE = "firstchoice_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f)

def get_live_information(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results: return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except: return None
    return None

# 4. Sidebar Setup
with st.sidebar:
    st.title("🏢 Firstchoice HQ")
    st.success("✅ Logged in securely")
    if st.button("➕ New J.A.R.V.I.S. Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        if "history_list" in st.session_state:
            st.session_state.history_list[st.session_state.current_chat_id] = []
            save_memory(st.session_state.history_list)
        st.rerun()

if "history_list" not in st.session_state:
    st.session_state.history_list = load_memory()
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []
    save_memory(st.session_state.history_list)

SYSTEM_PROMPT = """तुम 'Firstchoice J.A.R.V.I.S.' हो। तुम एक हाई-लेवल AI हो।
नियम: 
1. सीधा और सटीक जवाब दो।
2. <thinking> टैग्स में अपना लॉजिक लिखो।
3. यूज़र वॉयस से बात करे तो नेचुरल जवाब दो।"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT, generation_config=genai.types.GenerationConfig(temperature=0.2))

# 5. 🗂️ MAIN DASHBOARD TABS
tab1, tab2, tab3 = st.tabs(["🎙️ J.A.R.V.I.S. AI", "📊 CRM & Dashboard", "📄 Auto Document Creator"])

# --- TAB 1: J.A.R.V.I.S. AI (चैट, वॉइस, इंटरनेट, विज़न) ---
with tab1:
    st.title("J.A.R.V.I.S. AI Core 🧠")
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("🖼️ फोटो अपलोड करें", type=['png', 'jpg', 'jpeg'])
    with col2:
        st.markdown("🗣️ **'Hello FC' बोलकर कमांड दें:**")
        audio_bytes = audio_recorder(text="क्लिक करें...", recording_color="#e84118", neutral_color="#4cd137")

    current_messages = st.session_state.history_list[st.session_state.current_chat_id]
    for msg in current_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                text = msg["content"]
                tm = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
                if tm:
                    final_ans = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
                    with st.expander("🌌 Thinking...", expanded=False): st.markdown(f"*{tm.group(1).strip()}*")
                    st.markdown(final_ans)
                else: st.markdown(text)
            else: st.markdown(msg["content"])

    prompt = st.chat_input("कमांड टाइप करें...")
    
    if audio_bytes:
        with st.spinner("Processing Voice..."):
            with open("temp.wav", "wb") as f: f.write(audio_bytes)
            r = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                try:
                    raw_text = r.recognize_google(r.record(source), language="hi-IN").lower()
                    wake_words = ["hello fc", "हेलो एफसी", "hello f c", "हेलो fc"]
                    is_wake = any(ww in raw_text for ww in wake_words)
                    if is_wake:
                        for ww in wake_words: raw_text = raw_text.replace(ww, "").strip()
                        prompt = raw_text if raw_text else "जी बॉस, बताइए?"
                        st.success(f"🗣️ Wake Word Detected: {prompt}")
                    else: st.warning("⚠️ कमांड इग्नोर की गई। 'Hello FC' बोलें।")
                except: st.error("आवाज़ साफ़ नहीं आई।")

    if prompt:
        current_messages.append({"role": "user", "content": prompt})
        save_memory(st.session_state.history_list)
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🌍 Processing..."):
                try:
                    live_data = get_live_information(prompt)
                    final_prompt = f"Live Data:\n{live_data}\n\nQuery: {prompt}" if live_data else prompt
                    if uploaded_file:
                        response = model.generate_content([final_prompt, Image.open(uploaded_file)])
                    else:
                        response = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]).send_message(final_prompt)
                    
                    tm = re.search(r'<thinking>(.*?)</thinking>', response.text, re.DOTALL)
                    final_ans = re.sub(r'<thinking>.*?</thinking>', '', response.text, flags=re.DOTALL).strip()
                    if tm:
                        with st.expander("🌌 Thinking...", expanded=False): st.markdown(f"*{tm.group(1).strip()}*")
                    st.markdown(final_ans)
                    
                    clean_voice = re.sub(r'```.*?```', 'जानकारी स्क्रीन पर है।', final_ans, flags=re.DOTALL)
                    clean_voice = re.sub(r'[*#_]', '', clean_voice)
                    if clean_voice.strip():
                        tts = gTTS(text=clean_text_for_voice, lang='hi')
                        tts.save("reply.mp3")
                        st.audio("reply.mp3", format="audio/mp3", autoplay=True)
                    
                    current_messages.append({"role": "assistant", "content": response.text})
                    save_memory(st.session_state.history_list)
                except Exception as e: st.error(f"⚠️ एरर: {e}")

# --- TAB 2: CRM & DASHBOARD ---
with tab2:
    st.title("📊 Firstchoice CRM Dashboard")
    st.markdown("आपके सभी लोकल एस्टेट प्रोजेक्ट्स का लाइव स्टेटस।")
    
    # 📝 CRM Data Table
    crm_data = pd.DataFrame({
        "Project Name": ["City-1", "City-2 (Mohadi)", "Sai Samruddhi (City-3)", "City-4", "PropertyHub Platform"],
        "Status": ["Active", "Plotting Phase", "Layout Design", "Initial Planning", "Development"],
        "Total Plots/Vendors": [45, 120, 85, 0, 15],
        "Booked/Active": [38, 12, 40, 0, 5]
    })
    
    st.dataframe(crm_data, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Quick Action:** J.A.R.V.I.S. को कमांड दें: 'Mohadi प्रोजेक्ट का लेटेस्ट स्टेटस बताओ'")
    with col2:
        st.success("📈 **PropertyHub:** 5 Active Vendors Onboarded")

# --- TAB 3: AUTO PDF GENERATOR ---
with tab3:
    st.title("📄 Auto Document & Agreement Creator")
    st.markdown("सेकंडों में वेंडर एग्रीमेंट या इनवॉइस तैयार करें।")
    
    client_name = st.text_input("वेंडर / क्लाइंट का नाम")
    deal_amount = st.text_input("डील की रकम (Rs.)")
    project_select = st.selectbox("प्रोजेक्ट चुनें", ["City-1", "City-2 Mohadi", "Sai Samruddhi City-3", "City-4", "PropertyHub"])
    
    if st.button("Generate PDF Agreement"):
        if client_name and deal_amount:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="FIRSTCHOICE INFRA - OFFICIAL AGREEMENT", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="---------------------------------------------------------", ln=True, align='C')
            
            agreement_text = f"""
This agreement is made for the project: {project_select}.
            
Client/Vendor Name: {client_name}
Total Deal Amount: Rs. {deal_amount}/-
            
Authorized Signatory: Jitendra Govindrao Parate
Firm: Firstchoice Infra
            """
            pdf.multi_cell(0, 10, txt=agreement_text)
            
            pdf_file_name = f"Agreement_{client_name.replace(' ', '_')}.pdf"
            pdf.output(pdf_file_name)
            
            with open(pdf_file_name, "rb") as file:
                btn = st.download_button(
                    label="⬇️ Download PDF Agreement",
                    data=file,
                    file_name=pdf_file_name,
                    mime="application/pdf"
                )
            st.success("✅ PDF जनरेट हो गया!")
        else:
            st.error("कृपया क्लाइंट का नाम और रकम भरें।")
