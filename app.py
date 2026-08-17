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

# 1. Page Configuration
st.set_page_config(page_title="Global J.A.R.V.I.S.", page_icon="🌍", layout="wide")

# 2. API Key Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. 🧠 Permanent Memory System (लोकल डेटाबेस)
MEMORY_FILE = "firstchoice_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

# 🌐 4. Live Internet Search Function
def get_live_information(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                info = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                return info
    except:
        return None
    return None

# 5. Sidebar - Advanced UI
with st.sidebar:
    st.title("🌍 J.A.R.V.I.S. Global")
    st.success("✅ Engine: SONNET 5 + WEB SEARCH")
    
    st.markdown("### ⚙️ System Status")
    st.checkbox("🧠 Deep Thinking", value=True, disabled=True)
    st.checkbox("💾 Permanent Memory", value=True, disabled=True)
    st.checkbox("🎙️ Wake Word: 'Hello FC'", value=True, disabled=True) 
    st.checkbox("🌍 Live Internet", value=True, disabled=True) 
    
    st.divider()
    if st.button("➕ New Project / Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        save_memory(st.session_state.history_list)
        st.rerun()

    st.subheader("📁 Saved Projects")
    if "history_list" not in st.session_state:
        st.session_state.history_list = load_memory()
    
    for chat_id, messages in list(st.session_state.history_list.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(f"Chat {chat_id[:4]}", key=f"btn_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.rerun()
        if col2.button("🗑️", key=f"del_{chat_id}"):
            del st.session_state.history_list[chat_id]
            save_memory(st.session_state.history_list)
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = None
            st.rerun()

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []
    save_memory(st.session_state.history_list)

# 6. 🌌 THE MASTER SYSTEM PROMPT
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S.' हो। तुम एक ग्लोबल AI हो जिसकी पहुंच पूरी दुनिया के इंटरनेट और ज्ञान तक है।
तुम्हारे पास PropertyHub के डेवलपमेंट की नॉलेज भी है और दुनिया की हर जानकारी भी।

नियम:
1. 🌍 पल-भर में जवाब: दुनिया की कोई जानकारी पूछी जाए, सीधा और सटीक जवाब दो।
2. 🧠 डीप थिंकिंग: मुश्किल सवालों या कोडिंग से पहले <thinking> और </thinking> टैग्स में अपना लॉजिक लिखो।
3. 💻 फ्लॉलेस कोडिंग: बिना एरर के पूरा कोड दो।
4. 🗣️ वॉइस मोड: तुम बोलकर जवाब दे रहे हो, इसलिए जवाब नेचुरल और इंसान जैसा दो (ताकि सुनने में अच्छा लगे)।
5. 🎨 इमेज: फोटो मांगे जाने पर हमेशा ![Image](https://image.pollinations.ai/prompt/ENGLISH_PROMPT) यूज़ करो।
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(temperature=0.3) 
)

# 7. Main UI & Inputs
st.title("J.A.R.V.I.S. Global Intelligence 🌍")
st.markdown("**🗣️ 'Hello FC' बोलकर कमांड दें (जैसे: 'Hello FC, आज का मौसम बताओ')**")

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
                with st.expander("🌌 Thinking Process...", expanded=False):
                    st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
            else:
                st.markdown(text)
        else:
            st.markdown(msg["content"])

# 8. Text Input Logic
prompt = st.chat_input("या कमांड यहाँ टाइप करें...")

# 🗣️ Voice Input with "Hello FC" Wake Word Logic
if audio_bytes:
    with st.spinner("आवाज़ समझ रहा हूँ..."):
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio_data = r.record(source)
            try:
                raw_voice_text = r.recognize_google(audio_data, language="hi-IN")
                text_lower = raw_voice_text.lower()
                
                # चेक करें कि वाक्य में 'hello fc' या उससे मिलते-जुलते शब्द हैं या नहीं
                wake_words = ["hello fc", "हेलो एफसी", "hello f c", "हेलो fc", "हेलो फर्स्ट चॉइस", "hello first choice"]
                
                is_wake_word_detected = False
                for ww in wake_words:
                    if ww in text_lower:
                        is_wake_word_detected = True
                        # 'Hello FC' को हटाकर असली कमांड निकालना
                        prompt = text_lower.replace(ww, "").strip()
                        break
                
                if is_wake_word_detected:
                    if prompt == "":
                        prompt = "जी बॉस, बताइए मैं फर्स्टचॉइस इन्फ्रा के लिए क्या कर सकता हूँ?"
                    st.success(f"✅ Wake Word Detected: {prompt}")
                else:
                    st.warning(f"⚠️ सिस्टम ने आपको इग्नोर कर दिया। आपने कहा: '{raw_voice_text}' (कमांड से पहले 'Hello FC' बोलना ज़रूरी है!)")
                    prompt = None # कमांड आगे नहीं जाएगी
                    
            except:
                st.error("माफ़ करें, आवाज़ साफ़ नहीं आई। कृपया दोबारा बोलें।")

# 9. AI Processing, Internet Search & Voice Output
if prompt:
    current_messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.history_list)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🌍 जानकारी प्रोसेस कर रहा हूँ..."):
            try:
                # 🌐 लाइव इंटरनेट सर्च
                live_data = get_live_information(prompt)
                
                final_prompt = prompt
                if live_data:
                    final_prompt = f"यूज़र का सवाल: {prompt}\n\nलाइव इंटरनेट डेटा:\n{live_data}\n\nइस ताज़ा इंटरनेट डेटा का इस्तेमाल करके यूज़र को सबसे सटीक जवाब दो।"

                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([final_prompt, img])
                else:
                    gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                    chat_session = model.start_chat(history=gemini_history)
                    response = chat_session.send_message(final_prompt)
                
                response_text = response.text
                
                # UI Display
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_text, re.DOTALL)
                final_answer = response_text
                if thinking_match:
                    final_answer = re.sub(r'<thinking>.*?</thinking>', '', response_text, flags=re.DOTALL).strip()
                    with st.expander("🌌 Thinking Process...", expanded=False):
                        st.markdown(f"*{thinking_match.group(1).strip()}*")
                st.markdown(final_answer)
                
                # 🔊 TEXT TO SPEECH (आवाज़ में जवाब)
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
