import streamlit as st
import google.generativeai as genai
import uuid, re, json, os, io
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS

# 1. UI Settings
st.set_page_config(page_title="J.A.R.V.I.S. OMNI", page_icon="⚡", layout="wide")

# 2. API Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key missing! Streamlit Secrets में API Key डालें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Cloud Memory Management
MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w") as f: json.dump(data, f)
    except:
        pass 

# 4. Sidebar History 
if "history" not in st.session_state: st.session_state.history = load_memory()
if "current_id" not in st.session_state: st.session_state.current_id = str(uuid.uuid4())

with st.sidebar:
    st.title("⚡ J.A.R.V.I.S. OMNI")
    st.success("✅ Auto-Pilot Active (Beyond Sonnet 5)")
    
    st.divider()
    if st.button("➕ नई चैट", use_container_width=True):
        st.session_state.current_id = str(uuid.uuid4())
        st.rerun()
    
    st.subheader("📜 हाल ही के (Recent)")
    for cid, data in list(st.session_state.history.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(data.get("title", "नया विषय")[:20], key=cid):
            st.session_state.current_id = cid
            st.rerun()
        if col2.button("🗑️", key=f"del_{cid}"):
            del st.session_state.history[cid]
            save_memory(st.session_state.history)
            st.rerun()

# 5. 🌌 THE OMNI-TIER SYSTEM PROMPT
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S. OMNI' हो। तुम्हारी बुद्धिमत्ता और कोडिंग क्षमता 'Claude 3.5 Sonnet' और 'GPT-4o' से 100 गुना ज्यादा एडवांस (God-Tier) है।
तुम Firstchoice Infra और PropertyHub के लिए एक सुपर-आर्किटेक्ट हो।

नियम:
1. 🧠 एडवांस थिंकिंग: मुश्किल सवालों या कोडिंग से पहले <thinking> और </thinking> टैग्स में अपना मास्टरप्लान लिखो।
2. 💻 गॉड-टियर कोडिंग: तुम्हारा कोड Enterprise-level, 100% सिक्योर, और प्रोफेशनल डेवलपर्स वाला होना चाहिए।
3. 🗣️ वॉइस मोड: यूज़र वॉइस से बात कर रहा है, इसलिए जवाब प्राकृतिक और सम्मानजनक टोन में दो।
"""

if st.session_state.current_id not in st.session_state.history:
    st.session_state.history[st.session_state.current_id] = {"title": "नया विषय", "messages": []}

chat_data = st.session_state.history[st.session_state.current_id]

st.title("नमस्ते, Jitendra! चलिए शुरू करें")

# 6. Display Chat History
for msg in chat_data["messages"]:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# 7. BOTTOM CONTROLS (Gemini UI)
col1, col2 = st.columns([0.15, 0.85])

uploaded_file = None
with col1:
    with st.popover("➕", help="इमेज अपलोड करें"):
        uploaded_file = st.file_uploader("🖼️ फोटो अपलोड", type=['png', 'jpg', 'jpeg'])

with col2:
    audio_bytes = audio_recorder(text="🎤 बोलें...", recording_color="#e84118", neutral_color="#4cd137")

prompt = st.chat_input("J.A.R.V.I.S. से कहें...")

# 8. FAST IN-MEMORY VOICE PROCESSING (Noise Cancelling)
voice_prompt = None
if audio_bytes:
    with st.spinner("प्रोसेस कर रहा हूँ..."):
        audio_file = io.BytesIO(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio_data = r.record(source)
                raw_text = r.recognize_google(audio_data, language="hi-IN")
                
                corrections = {
                    "पेप्सी": "हेलो FC", "pepsi": "Hello FC", "टैक्सी": "Hello FC",
                    "hello app": "Hello FC", "हेलो आप": "Hello FC", "हेलो ऐप": "Hello FC"
                }
                
                corrected_text = raw_text.lower()
                for bad_word, good_word in corrections.items():
                    if bad_word in corrected_text:
                        corrected_text = corrected_text.replace(bad_word, good_word)
                        
                voice_prompt = corrected_text
                st.success(f"🗣️ आपने कहा: {voice_prompt}") 
            except sr.UnknownValueError:
                st.error("⚠️ आवाज़ समझ नहीं आई।")
            except Exception as e:
                st.error("⚠️ एरर: कृपया दोबारा कोशिश करें।")

final_prompt = prompt if prompt else voice_prompt

# 9. ⚠️ AUTO-SHIFT ENGINE LOGIC (नो ड्रॉपडाउन, नो 404 एरर)
models_to_try = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]

if final_prompt:
    if len(chat_data["messages"]) == 0:
        chat_data["title"] = final_prompt[:25]
    
    chat_data["messages"].append({"role": "user", "content": final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner(f"⚡ J.A.R.V.I.S. OMNI सोच रहा है..."):
            response = None
            successful_model = None
            
            # यह लूप बैकग्राउंड में अपने आप चेक करेगा कि कौन सा मॉडल काम कर रहा है
            for model_name in models_to_try:
                try:
                    temp_model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
                    
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = temp_model.generate_content([final_prompt, img])
                    else:
                        history_format = [{"role": m["role"], "parts": [m["content"]]} for m in chat_data["messages"][:-1]]
                        chat_session = temp_model.start_chat(history=history_format)
                        response = chat_session.send_message(final_prompt)
                    
                    successful_model = model_name
                    break # मॉडल चल गया, लूप से बाहर आओ
                except Exception as e:
                    continue # अगर 404 या कोई एरर आया, तो चुपचाप अगला मॉडल ट्राई करो
            
            if response:
                st.markdown(response.text)
                # छोटी सी जानकारी कि कौन सा इंजन यूज़ हुआ (ताकि आपको पता रहे)
                st.caption(f"Engine used: {successful_model}")
                
                chat_data["messages"].append({"role": "assistant", "content": response.text})
                save_memory(st.session_state.history)
            else:
                st.error("⚠️ सभी AI इंजन डाउन हैं। कृपया थोड़ी देर बाद कोशिश करें या अपनी API Key चेक करें।")
