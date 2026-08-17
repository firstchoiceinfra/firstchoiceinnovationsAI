import streamlit as st
import google.generativeai as genai

# 1. Claude जैसा प्रोफेशनल डिज़ाइन
st.set_page_config(page_title="Firstchoice AI Coder", page_icon="⚡", layout="wide")

# 2. Sidebar - अरेंज्ड और व्यवस्थित
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    st.caption("Multilingual Coding Edition (HI/EN/MR)")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()
        
    st.divider()
    st.info("💡 मैं आपकी भाषा समझता हूँ! सवाल हिंदी, मराठी या इंग्लिश में पूछें।")

st.title("मैं आपकी क्या मदद कर सकता हूँ?")

# 3. API सेटअप
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key मिसिंग है!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 4. Multilingual System Prompt
SYSTEM_PROMPT = """
तुम दुनिया के सबसे बेहतरीन सॉफ्टवेयर आर्किटेक्ट हो। 
तुम्हारी सबसे बड़ी खूबी यह है कि तुम यूज़र की भाषा (हिंदी, मराठी या इंग्लिश) को तुरंत पहचान लेते हो। 
जिस भाषा में यूज़र सवाल पूछे, तुम्हें उसी भाषा में कोडिंग और तकनीकी जवाब देना है। 
अगर यूज़र मराठी में पूछे, तो मराठी में जवाब दो। हिंदी में पूछे तो हिंदी में, और इंग्लिश में पूछे तो इंग्लिश में। 
सिर्फ सटीक कोड और समाधान दो, फालतू बातें मत करना।
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=SYSTEM_PROMPT
)

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# 6. Chat Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Chat Input
if prompt := st.chat_input("अपना सवाल यहाँ लिखें (Type your question here)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Generating answer..."):
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
