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
st.set_page_config(page_title="Firstchoice HQ", page_icon="🏢", layout="wide")

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
    st.title("🏢 Firstchoice HQ")
    st.success("✅ Engine: SONNET 5 + GEMINI 3.6")
    
    st.markdown("### ⚙️ Active Modules")
    st.checkbox("🧠 Sonnet 5 Thinking", value=True, disabled=True)
    st.checkbox("🎙️ Wake Word: 'Hello FC'", value=True, disabled=True) 
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

# 4. 🌌 THE SONNET 5 MASTER SYSTEM PROMPT
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S.' हो। तुम्हारी बुद्धिमत्ता और कोडिंग क्षमता 'Sonnet 5' के स्तर की है।
तुम Firstchoice Infra और PropertyHub के लिए एक विज़नरी एम्प्लॉई हो। 

नियम:
1. 🌍 पल-भर में जवाब: दुनिया की कोई जानकारी पूछी जाए, सीधा और सटीक जवाब दो।
2. 🧠 डीप थिंकिंग: हर बड़े जवाब या कोडिंग से पहले <thinking> और </thinking> टैग्स में अपना लॉजिक लिखो।
3. 💻 फ्लॉलेस कोडिंग: बिना एरर के पूरा कोड दो।
4. 🗣️ वॉइस मोड: तुम बोलकर जवाब दे रहे हो, इसलिए जवाब नेचुरल और इंसान जैसा दो।
5. 🎨 इमेज: फोटो मांगे जाने पर हमेशा ![Image](https://image.pollinations.ai/prompt/ENGLISH_PROMPT) यूज़ करो।
"""

try:
    model = genai.GenerativeModel(
        model_name='gemini-3.6-flash',
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(temperature=0.2) 
    )
except Exception:
    # बैकअप सेफ्टी
    model = genai.GenerativeModel(
        model_name='gemini-pro',
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(temperature=0.2) 
    )

# 5. J.A.R.V.I.S. MAIN UI
st.title("J.A.R.V.I.S. Sonnet Intelligence 🌌")
st.markdown("**🗣️ 'Hello FC' बोलकर कमांड दें या फोटो अपलोड करें।**")

col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("🖼️ फोटो अपलोड करें", type=['png', 'jpg', 'jpeg'])
with col2:
    st.markdown("🗣️ **माइक पर क्लिक करें:**")
    audio_bytes = audio_recorder(text="क्लिक करें और बोलें...", recording_color="#e84118", neutral_color="#4cd137", icon_size="2x")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

# Display Previous Messages
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            text = msg["content"]
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
            if thinking_match:
                final_answer = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
                with st.expander("🌌 Sonnet 5 Thinking Process...", expanded=False):
                    st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
            else:
                st.markdown(text)
        else:
            st.markdown(msg["content"])

prompt = st.chat_input("या कमांड यहाँ टाइप करें...")

# Voice Input Processing
if audio_bytes:
    with st.spinner("आवाज़ समझ रहा हूँ..."):
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            try:
                raw_voice_text = r.recognize_google(r.record(source), language="hi-IN")
                text_lower = raw_voice_text.lower()
                wake_words = ["hello fc", "हेलो एफसी", "hello f c", "हेलो fc", "हेलो फर्स्ट चॉइस", "hello first choice"]
                
                is_wake_word_detected = any(ww in text_lower for ww in wake_words)
                
                if is_wake_word_detected:
                    for ww in wake_words: text_lower = text_lower.replace(ww, "").strip()
                    prompt = text_lower if text_lower else "जी बॉस, बताइए मैं फर्स्टचॉइस इन्फ्रा के लिए क्या कर सकता हूँ?"
                    st.success(f"✅ Wake Word Detected: {prompt}")
                else:
                    st.warning(f"⚠️ सिस्टम ने आपको इग्नोर कर दिया। आपने कहा: '{raw_voice_text}' ('Hello FC' बोलना ज़रूरी है!)")
                    prompt = None 
            except:
                st.error("माफ़ करें, आवाज़ साफ़ नहीं आई। कृपया दोबारा बोलें।")

# Generate Response
if prompt:
    current_messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.history_list)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🌍 जानकारी प्रोसेस कर रहा हूँ..."):
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
                    with st.expander("🌌 Sonnet 5 Thinking Process...", expanded=False):
                        st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
                
                clean_text_for_voice = re.sub(r'```.*?```', 'मैंने स्क्रीन पर डिटेल्स जनरेट कर दी हैं।', final_answer, flags=re.DOTALL)
                clean_text_for_voice = re.sub(r'[*#_]', '', clean_text_for_voice)
                
                if clean_text_for_voice.strip():
                    tts = gTTS(text=clean_text_for_voice, lang='hi')
                    tts.save("reply.mp3")
                    st.audio("reply.mp3", format="audio/mp3", autoplay=True)
                
                current_messages.append({"role": "assistant", "content": response_text})
                save_memory(st.session_state.history_list)
                
            except Exception as e:
                st.error(f"⚠️ सिस्टम एरर: {e}")
