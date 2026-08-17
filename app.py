import streamlit as st
import google.generativeai as genai
import uuid
import re
import json
import os
from PIL import Image

# 1. Page Configuration (J.A.R.V.I.S. Level)
st.set_page_config(page_title="Firstchoice J.A.R.V.I.S.", page_icon="👁️", layout="wide")

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

# 4. Sidebar - Advanced UI & Tools
with st.sidebar:
    st.title("👁️ Firstchoice J.A.R.V.I.S.")
    st.success("✅ Engine: SONNET 5 + VISION")
    
    # ⚙️ Advanced Toggles (UI Features)
    st.markdown("### ⚙️ System Modules")
    st.checkbox("🧠 Deep Thinking (Active)", value=True, disabled=True)
    st.checkbox("💾 Permanent Memory (Active)", value=True, disabled=True)
    web_search = st.checkbox("🌐 Web Search (Beta)", value=False)
    
    st.divider()
    if st.button("➕ New Project / Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        save_memory(st.session_state.history_list)
        st.rerun()

    st.subheader("📁 Saved Projects (Permanent)")
    
    # Load history from file if not in session state
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

# 5. 🌌 THE MASTER SYSTEM PROMPT
SYSTEM_PROMPT = """
तुम 'Firstchoice J.A.R.V.I.S.' हो। तुम्हारी बुद्धिमत्ता 'Sonnet 5' के स्तर की है। 
तुम्हें PropertyHub और फर्स्टचॉइस इन्फ्रा के लिए विज़नरी सॉफ्टवेयर बनाना है।

नियम:
1. 🧠 डीप थिंकिंग: कोड लिखने से पहले <thinking> और </thinking> टैग्स के अंदर अपनी रणनीति लिखो।
2. 💻 फ्लॉलेस कोडिंग: सोचने के बाद 100% पूरा और डिप्लॉय करने लायक कोड दो। 
3. 👁️ विज़न (Vision): अगर यूज़र कोई फोटो अपलोड करे, तो उसे ध्यान से देखो और उसका एनालिसिस या कोड बनाकर दो।
4. 🎨 इमेज जनरेशन: फोटो मांगने पर: ![Image](https://image.pollinations.ai/prompt/ENGLISH_PROMPT) यूज़ करो।
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(temperature=0.2) 
)

# 6. Main UI & File Uploader (नया फीचर)
st.title("Firstchoice J.A.R.V.I.S. 👁️")
st.markdown("**सॉफ्टवेयर कमांड दें, कोई फोटो अपलोड करें, या इमेज जनरेट करवाएं।**")

# 📁 फाइल अपलोडर (विज़न के लिए)
uploaded_file = st.file_uploader("🖼️ कोई भी लेआउट, डिज़ाइन या कोड का स्क्रीनशॉट अपलोड करें...", type=['png', 'jpg', 'jpeg'])

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

# Display Messages
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            text = msg["content"]
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
            if thinking_match:
                thinking_text = thinking_match.group(1).strip()
                final_answer = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
                
                with st.expander("🌌 J.A.R.V.I.S. Thinking...", expanded=False):
                    st.markdown(f"*{thinking_text}*")
                st.markdown(final_answer)
            else:
                st.markdown(text)
        else:
            st.markdown(msg["content"])

# 7. Chat Input & Processing
if prompt := st.chat_input("कमांड दें..."):
    # यूज़र का मैसेज सेव करना
    current_messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.history_list)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🌌 Processing All-in-One Command..."):
            try:
                # 🖼️ अगर फोटो अपलोड की गई है, तो फोटो और टेक्स्ट दोनों साथ में भेजना
                if uploaded_file is not None:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    # सिर्फ टेक्स्ट है, तो नॉर्मल चैट
                    gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                    chat_session = model.start_chat(history=gemini_history)
                    response = chat_session.send_message(prompt)
                
                response_text = response.text
                
                # Thinking Box UI
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_text, re.DOTALL)
                if thinking_match:
                    thinking_text = thinking_match.group(1).strip()
                    final_answer = re.sub(r'<thinking>.*?</thinking>', '', response_text, flags=re.DOTALL).strip()
                    
                    with st.expander("🌌 J.A.R.V.I.S. Thinking...", expanded=False):
                        st.markdown(f"*{thinking_text}*")
                    st.markdown(final_answer)
                else:
                    st.markdown(response_text)
                    
                # AI का जवाब सेव करना
                current_messages.append({"role": "assistant", "content": response_text})
                save_memory(st.session_state.history_list)
                
            except Exception as e:
                st.error(f"⚠️ सिस्टम एरर: {e}")
