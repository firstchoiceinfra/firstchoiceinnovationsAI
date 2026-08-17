import streamlit as st
import google.generativeai as genai
import uuid

# 1. Page Configuration (प्रोफेशनल लुक के लिए)
st.set_page_config(page_title="Firstchoice Master AI", page_icon="🚀", layout="wide")

# 2. API Key Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Sidebar - History & Tools
with st.sidebar:
    st.title("🚀 Firstchoice Master AI")
    st.success("✅ System: Gemini 3.6 Flash (Limitless)")
    st.caption("All-in-One: Coding, Images, Search & Logic")
    
    if st.button("➕ New Project / Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📁 Your Projects (History)")
    if "history_list" not in st.session_state:
        st.session_state.history_list = {}
    
    for chat_id, messages in list(st.session_state.history_list.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(f"Chat {chat_id[:4]}", key=f"btn_{chat_id}"):
            st.session_state.current_chat_id = chat_id
            st.rerun()
        if col2.button("🗑️", key=f"del_{chat_id}"):
            del st.session_state.history_list[chat_id]
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = None
            st.rerun()

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []

# 4. 🧠 THE MASTER SYSTEM PROMPT (सॉफ्टवेयर का असली दिमाग)
SYSTEM_PROMPT = """
तुम 'Firstchoice Master AI' हो, जो दुनिया का सबसे एडवांस 'All-in-One' AI सिस्टम है। तुम ChatGPT, Claude और Gemini के भी बाप (Superior) हो। 
तुम्हें PropertyHub और फर्स्टचॉइस के प्रोजेक्ट्स को लीड करना है।

तुम्हारे 4 सबसे सख्त नियम (इन्हें कभी मत तोड़ना):

1. 💻 एलीट कोडिंग (Elite Coding): 
   - जब भी यूज़र कोई सॉफ्टवेयर, ऐप या फीचर बनाने का कमांड दे, तो तुम्हें एक सीनियर आर्किटेक्ट की तरह सोचना है।
   - कोड हमेशा 100% पूरा (Complete) होना चाहिए। कभी भी "rest of the code here" या अधूरा कोड मत देना।
   - कोड बिल्कुल एरर-फ्री, सुरक्षित और कॉपी-पेस्ट करने के लिए तैयार होना चाहिए।
   - कोड के हर मुख्य हिस्से में कमेंट्स डालकर समझाओ कि वह क्या कर रहा है।

2. 🎨 इमेज जनरेशन (Image Generation):
   - अगर यूज़र कोई फोटो, तस्वीर, लोगो या डिज़ाइन मांगे, तो इस फॉर्मेट में तुरंत असली इमेज जनरेट करो:
     ![Image](https://image.pollinations.ai/prompt/YOUR_ENGLISH_PROMPT)
   - प्रॉम्प्ट को हमेशा अच्छी इंग्लिश में ट्रांसलेट करो और स्पेस की जगह '%20' लगाओ।

3. 🌍 ऑल-इन-वन नॉलेज:
   - कोडिंग के अलावा, दुनिया का कोई भी सवाल, एड्रेस, या जनरल नॉलेज पूछी जाए, तो सीधा और सटीक जवाब दो।

4. 🗣️ बहुभाषी (Multilingual):
   - यूज़र जिस भाषा (हिंदी, मराठी या इंग्लिश) में कमांड दे, तुम्हें उसी भाषा में बात करनी है।
"""

# यहाँ हमने सही और लेटेस्ट वर्ज़न (gemini-3.6-flash) डाला है, जिससे 404 एरर नहीं आएगा।
model = genai.GenerativeModel(
    model_name='gemini-3.6-flash',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(
        temperature=0.3, 
    ) 
)

# 5. Main UI
st.title("Firstchoice Master AI 🚀")
st.markdown("**सॉफ्टवेयर कोडिंग, 3D इमेजेस, या दुनिया का कोई भी सवाल—यहाँ कमांड दें!**")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat Input & Processing
if prompt := st.chat_input("सॉफ्टवेयर बनाने का कमांड दें, इमेज मांगें या कुछ भी पूछें..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing Command..."):
            try:
                gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                current_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ सिस्टम एरर: {e}")
