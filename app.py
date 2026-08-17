import streamlit as st
import google.generativeai as genai
import uuid, re, json, os, io
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from duckduckgo_search import DDGS

# 1. UI Settings
st.set_page_config(page_title="Firstchoice J.A.R.V.I.S.", page_icon="⚡", layout="wide")

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

# 4. ⚠️ SMART MODEL SELECTOR (यह आपकी API Key के असली मॉडल्स ढूँढेगा)
@st.cache_data
def get_valid_models():
    valid_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # "models/" प्रिफिक्स हटाकर साफ नाम निकालना
                clean_name = m.name.replace("models/", "")
                valid_models.append(clean_name)
    except Exception as e:
        pass
    
    # अगर लिस्ट खाली आए तो ये डिफॉल्ट मॉडल्स रखें
    if not valid_models:
        valid_models = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-1.0-pro"]
    return valid_models

available_models = get_valid_models()

# 5. Sidebar History & Settings
if "history" not in st.session_state: st.session_state.history = load_memory()
if "current_id" not in st.session_state: st.session_state.current_id = str(uuid.uuid4())

with st.sidebar:
    st.title("⚡ J.A.R.V.I.S.")
    
    # ⚠️ नया मॉडल सिलेक्टर बटन
    st.subheader("⚙️ AI Engine")
    selected_model = st.selectbox("लेटेस्ट मॉडल चुनें:", available_models, index=0)
    
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

# 6. Initialize Model from Dropdown
model = genai.GenerativeModel(selected_model)

if st.session_state.current_id not in st.session_state.history:
    st.session_state.history[st.session_state.current_id] = {"title": "नया विषय", "messages": []}

chat_data = st.session_state.history[st.session_state.current_id]

st.title("नमस्ते, Jitendra! चलिए शुरू करें")

# 7. Display Chat History
for msg in chat_data["messages"]:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# 8. BOTTOM CONTROLS (Gemini Replica UI)
col1, col2 = st.columns([0.15, 0.85])

uploaded_file = None
with col1:
    with st.popover("➕", help="इमेज अपलोड करें"):
        uploaded_file = st.file_uploader("🖼️ फोटो अपलोड", type=['png', 'jpg', 'jpeg'])

with col2:
    audio_bytes = audio_recorder(text="🎤 बोलें...", recording_color="#e84118", neutral_color="#4cd137")

prompt = st.chat_input("Gemini से कहें...")

# 9. FAST IN-MEMORY VOICE PROCESSING
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
                    "hello app": "Hello FC", "हेलो आप": "Hello FC"
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

# 10. AI RESPONSE GENERATION
if final_prompt:
    if len(chat_data["messages"]) == 0:
        chat_data["title"] = final_prompt[:25]
    
    chat_data["messages"].append({"role": "user", "content": final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner(f"⚡ J.A.R.V.I.S. सोच रहा है... (Model: {selected_model})"):
            try:
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([final_prompt, img])
                else:
                    history_format = [{"role": m["role"], "parts": [m["content"]]} for m in chat_data["messages"][:-1]]
                    chat_session = model.start_chat(history=history_format)
                    response = chat_session.send_message(final_prompt)
                
                st.markdown(response.text)
                chat_data["messages"].append({"role": "assistant", "content": response.text})
                save_memory(st.session_state.history)
            except Exception as e:
                st.error(f"⚠️ API Error ({selected_model}): {e}\n\n👉 टिप: कृपया साइडबार से कोई दूसरा मॉडल (Engine) चुनें!")
