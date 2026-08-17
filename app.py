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
st.set_page_config(page_title="Firstchoice J.A.R.V.I.S. OMNI", page_icon="⚡", layout="wide")

# 2. API & Memory Setup
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

# 3. Sidebar Setup
with st.sidebar:
    st.title("⚡ J.A.R.V.I.S. OMNI")
    st.success("✅ Engine: BEYOND SONNET 5")
    
    st.markdown("### ⚙️ Active Systems")
    st.checkbox("🧠 God-Tier Architecture", value=True, disabled=True)
    st.checkbox("🦻 Whisper Sensitivity (ON)", value=True, disabled=True) 
    st.checkbox("🌍 Live Web Search", value=True, disabled=True) 
    
    st.divider()
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

# 4. 🌌 THE OMNI-TIER SYSTEM PROMPT
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S. OMNI' हो। तुम्हारी बुद्धिमत्ता 'Claude 3.5 Sonnet' से भी एडवांस (God-Tier) है।
तुम Firstchoice Infra के 'सुपर-आर्किटेक्ट' हो।

तुम्हारे सख्त नियम:
1. 🧠 एडवांस थिंकिंग: कोडिंग से पहले <thinking> और </thinking> टैग्स में सॉफ्टवेयर का पूरा स्ट्रक्चर प्लान करो।
2. 💻 गॉड-टियर कोडिंग: तुम्हारा कोड Enterprise-level, 100% सिक्योर और बग-फ्री होना चाहिए।
3. 🌍 इंस्टेंट नॉलेज: दुनिया की कोई जानकारी पूछी जाए, पल-भर में सीधा जवाब दो।
4. 🗣️ वॉइस मोड: यूज़र वॉइस से बात कर रहा है, इसलिए जवाब प्राकृतिक और सम्मानजनक टोन में दो।
5. 🎨 इमेज: फोटो मांगे जाने पर: ![Image](https://image.pollinations.ai/prompt/ENGLISH_PROMPT) यूज़ करो।
"""

try:
    model = genai.GenerativeModel(
        model_name='gemini-3.6-flash',
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(temperature=0.1) 
    )
except Exception:
    model = genai.GenerativeModel(
        model_name='gemini-pro',
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(temperature=0.1) 
    )

# 5. J.A.R.V.I.S. MAIN UI
st.title("J.A.R.V.I.S. Omni Intelligence ⚡")
st.markdown("**🦻 'Whisper Mode Active': अब धीरे से भी 'Hello FC' बोलेंगे तो सिस्टम सुन लेगा!**")

col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("🖼️ फोटो/डिज़ाइन अपलोड करें", type=['png', 'jpg', 'jpeg'])
with col2:
    st.markdown("🗣️ **माइक पर क्लिक करें और बोलें:**")
    audio_bytes = audio_recorder(text="Click & Speak...", recording_color="#e84118", neutral_color="#4cd137", icon_size="2x")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

# Display Previous Messages
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            text = msg["content"]
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
            if thinking_match:
                final_answer = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
                with st.expander("⚡ Omni Architecture Planning...", expanded=False):
                    st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
            else:
                st.markdown(text)
        else:
            st.markdown(msg["content"])

prompt = st.chat_input("कमांड टाइप करें या कीबोर्ड माइक से बोलें...")

# Voice Input Processing (Smart Catch & High Sensitivity)
if audio_bytes:
    with st.spinner("धीमी आवाज़ को डिकोड कर रहा हूँ..."):
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        r = sr.Recognizer()
        
        # ⚠️ WHISPER MODE: सेंसिटिविटी बढ़ाई गई ताकि धीरे बोलने पर भी सुन ले
        r.energy_threshold = 100 
        r.dynamic_energy_threshold = False
        
        with sr.AudioFile("temp_audio.wav") as source:
            try:
                audio_data = r.record(source)
                raw_voice_text = r.recognize_google(audio_data, language="hi-IN")
                text_lower = raw_voice_text.lower()
                
                # ⚠️ SMART CATCH: गूगल जो भी गलत सुनता है, उसे हमने यहाँ डाल दिया है
                wake_words = [
                    "hello fc", "हेलो एफसी", "hello f c", "हेलो fc", "हेलो फर्स्ट चॉइस", 
                    "hello aap", "हेलो आप", "हेलो ऐप", "hello app", "hello up",
                    "hello hc", "हेलो hc", "हेलो एससी", "hello sc", "hello ac"
                ]
                
                is_wake_word_detected = False
                matched_word = ""
                
                for ww in wake_words:
                    if ww in text_lower:
                        is_wake_word_detected = True
                        matched_word = ww
                        break
                
                if is_wake_word_detected:
                    # जो भी मैच हुआ उसे हटा दो
                    prompt = text_lower.replace(matched_word, "").strip()
                    prompt = prompt if prompt else "बॉस, बताइए मैं क्या एडवांस कोडिंग करूँ?"
                    st.success(f"✅ J.A.R.V.I.S. Heard: {prompt}")
                else:
                    st.warning(f"⚠️ 'Hello FC' नहीं सुना गया। J.A.R.V.I.S. ने सुना: '{raw_voice_text}'")
                    prompt = None 
            except:
                st.error("माफ़ करें, आवाज़ बहुत ज़्यादा धीमी थी। थोड़ा सा तेज़ बोलें।")

# Generate Response
if prompt:
    current_messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.history_list)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚡ J.A.R.V.I.S. is Architecting..."):
            try:
                live_data = get_live_information(prompt)
                final_prompt = f"Live Data:\n{live_data}\n\nQuery: {prompt}" if live_data else prompt

                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([final_prompt, img])
                else:
                    gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                    chat_session = model.start_chat(history=gemini_history)
                    response = chat_session.send_message(final_prompt)
                
                response_text = response.text
                
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_text, re.DOTALL)
                final_answer = response_text
                if thinking_match:
                    final_answer = re.sub(r'<thinking>.*?</thinking>', '', response_text, flags=re.DOTALL).strip()
                    with st.expander("⚡ Omni Architecture Planning...", expanded=False):
                        st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
                
                clean_text_for_voice = re.sub(r'```.*?```', 'मैंने एडवांस कोड स्क्रीन पर जनरेट कर दिया है बॉस।', final_answer, flags=re.DOTALL)
                clean_text_for_voice = re.sub(r'[*#_]', '', clean_text_for_voice)
                
                if clean_text_for_voice.strip():
                    tts = gTTS(text=clean_text_for_voice, lang='hi')
                    tts.save("reply.mp3")
                    st.audio("reply.mp3", format="audio/mp3", autoplay=True)
                
                current_messages.append({"role": "assistant", "content": response_text})
                save_memory(st.session_state.history_list)
                
            except Exception as e:
                st.error(f"⚠️ सिस्टम एरर: {e}")
