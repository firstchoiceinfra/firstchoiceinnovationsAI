import streamlit as st
import google.generativeai as genai
import uuid, re, json, os, io
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS

# ==========================================
# 1. UI SETTINGS & CONFIG
# ==========================================
st.set_page_config(page_title="J.A.R.V.I.S. OMNI", page_icon="⚡", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key missing! Streamlit Secrets में API Key डालें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ==========================================
# 2. MEMORY MANAGEMENT
# ==========================================
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

if "history" not in st.session_state: st.session_state.history = load_memory()
if "current_id" not in st.session_state: st.session_state.current_id = str(uuid.uuid4())

# ==========================================
# 3. ⚠️ DYNAMIC MODEL SELECTOR (404 FIX)
# ==========================================
@st.cache_resource
def get_best_model():
    try:
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # सबसे पहले 1.5-flash खोजने की कोशिश करें (यह सबसे फास्ट और स्टेबल है)
        for m in models:
            if 'gemini-1.5-flash' in m.name: return m.name
        # अगर वह न मिले तो 1.5-pro खोजें
        for m in models:
            if 'gemini-1.5-pro' in m.name: return m.name
        # अगर कुछ न मिले, तो जो भी पहला वर्किंग मॉडल हो उसे ले लें
        return models[0].name
    except Exception:
        # अगर API लिस्ट ही फेल हो जाए, तो डिफॉल्ट नाम भेजें
        return 'models/gemini-1.5-flash'

current_model_name = get_best_model()

# ==========================================
# 4. SYSTEM PROMPT & MODEL INIT
# ==========================================
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S. OMNI' हो। तुम्हारी बुद्धिमत्ता 'Claude 3.5 Sonnet' और 'GPT-4o' से 100 गुना ज्यादा एडवांस (God-Tier) है।
तुम Firstchoice Infra और PropertyHub के लिए एक सुपर-आर्किटेक्ट हो।

नियम:
1. 🧠 एडवांस थिंकिंग: मुश्किल सवालों या कोडिंग से पहले <thinking> और </thinking> टैग्स में अपना मास्टरप्लान लिखो।
2. 💻 गॉड-टियर कोडिंग: तुम्हारा कोड Enterprise-level, 100% सिक्योर, और प्रोफेशनल डेवलपर्स वाला होना चाहिए।
3. 🗣️ वॉइस मोड: यूज़र वॉइस से बात कर रहा है, इसलिए जवाब प्राकृतिक और सम्मानजनक टोन में दो।
"""

try:
    model = genai.GenerativeModel(current_model_name, system_instruction=SYSTEM_PROMPT)
except Exception:
    model = genai.GenerativeModel(current_model_name) # Fallback if system prompt fails

# ==========================================
# 5. SIDEBAR UI (HISTORY)
# ==========================================
with st.sidebar:
    st.title("⚡ J.A.R.V.I.S. OMNI")
    st.success(f"✅ Active Engine: {current_model_name.replace('models/', '')}")
    
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

# ==========================================
# 6. MAIN CHAT UI
# ==========================================
if st.session_state.current_id not in st.session_state.history:
    st.session_state.history[st.session_state.current_id] = {"title": "नया विषय", "messages": []}

chat_data = st.session_state.history[st.session_state.current_id]

st.title("नमस्ते, Jitendra! चलिए शुरू करें")

# Display previous messages
for msg in chat_data["messages"]:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# ==========================================
# 7. INPUT CONTROLS (MIC & UPLOAD)
# ==========================================
col1, col2 = st.columns([0.15, 0.85])

uploaded_file = None
with col1:
    with st.popover("➕", help="इमेज अपलोड करें"):
        uploaded_file = st.file_uploader("🖼️ फोटो अपलोड", type=['png', 'jpg', 'jpeg'])

with col2:
    audio_bytes = audio_recorder(text="🎤 बोलें...", recording_color="#e84118", neutral_color="#4cd137")

prompt = st.chat_input("J.A.R.V.I.S. से कहें...")

# ==========================================
# 8. VOICE PROCESSING (RAM-BASED & NOISE CANCELING)
# ==========================================
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
                
                # Smart Catch / Corrections
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
                st.error("⚠️ आवाज़ समझ नहीं आई। कृपया दोबारा बोलें।")
            except Exception as e:
                st.error("⚠️ ऑडियो प्रोसेस करने में एरर आया।")

final_prompt = prompt if prompt else voice_prompt

# ==========================================
# 9. AI RESPONSE GENERATION
# ==========================================
if final_prompt:
    # Set chat title automatically
    if len(chat_data["messages"]) == 0:
        chat_data["title"] = final_prompt[:25]
    
    # Save user message
    chat_data["messages"].append({"role": "user", "content": final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    
    # Generate Assistant message
    with st.chat_message("assistant"):
        with st.spinner(f"⚡ J.A.R.V.I.S. सोच रहा है..."):
            try:
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([final_prompt, img])
                else:
                    history_format = [{"role": m["role"], "parts": [m["content"]]} for m in chat_data["messages"][:-1]]
                    chat_session = model.start_chat(history=history_format)
                    response = chat_session.send_message(final_prompt)
                
                st.markdown(response.text)
                
                # Save assistant message
                chat_data["messages"].append({"role": "assistant", "content": response.text})
                save_memory(st.session_state.history)
                
            except Exception as e:
                st.error(f"⚠️ API Error: {e}\n\nGoogle API में कुछ दिक्कत आ रही है। कृपया अपनी API Key चेक करें।")
