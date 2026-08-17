import streamlit as st
import google.generativeai as genai

# ऐप का लुक और टाइटल
st.set_page_config(page_title="Custom AI Coder", layout="wide", page_icon="💻")
st.title("💻 Limitless AI Coding Assistant")

# Streamlit के 'Secrets' से API Key लेना (सुरक्षा के लिए)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("⚠️ API Key नहीं मिली! कृपया इसे Streamlit की Settings (Secrets) में सेट करें।")
    st.stop()

# AI को निर्देश देना कि उसे कैसे काम करना है (System Prompt)
SYSTEM_INSTRUCTION = """
तुम दुनिया के सबसे बेहतरीन Python और Streamlit सॉफ्टवेयर डेवलपर हो।
मैं पूरे इंडिया के लिए एक यूनीक रियल एस्टेट और वेंडर सर्विस प्लेटफ़ॉर्म (PropertyHub) बना रहा हूँ।
मुझे हमेशा सीधा, बिना एरर वाला, और पूरी तरह से ऑप्टिमाइज़्ड कोड लिखकर दो। कोई फालतू बात मत करना।
"""

# AI मॉडल सेट अप करना
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=SYSTEM_INSTRUCTION
)

# पुरानी चैट हिस्ट्री सेव रखने के लिए
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_session = model.start_chat(history=[])

# पुरानी बातचीत को स्क्रीन पर दिखाना
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

# यूज़र (आपसे) इनपुट लेना
user_input = st.chat_input("अपना कोडिंग का सवाल यहाँ पूछें...")

if user_input:
    # आपका मैसेज दिखाना
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    # AI का जवाब जनरेट करना
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        # API को कॉल करना
        response = st.session_state.chat_session.send_message(user_input)
        response_placeholder.markdown(response.text)
    
    st.session_state.chat_history.append({"role": "assistant", "text": response.text})

