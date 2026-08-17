import streamlit as st
import google.generativeai as genai

# 1. Claude जैसा प्रोफेशनल और वाइड (Wide) डिज़ाइन
st.set_page_config(page_title="Firstchoice AI Coder", page_icon="⚡", layout="wide")

# 2. Sidebar (साइडबार) - बिल्कुल Claude की तरह अरेंज्ड
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    st.caption("Limitless Coding Edition")
    
    # 'New Chat' बटन (पुरानी चैट क्लियर करने के लिए)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()
        
    st.divider()
    st.success("🟢 Status: No Limits")
    st.info("System: यह AI खास तौर पर PropertyHub जैसे बड़े सॉफ्टवेयर और रियल एस्टेट प्लेटफॉर्म्स की कोडिंग के लिए कस्टमाइज़ किया गया है।")

# मुख्य स्क्रीन का टाइटल
st.title("मैं आपकी क्या मदद कर सकता हूँ?")

# 3. API और सिक्योरिटी सेटअप
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Streamlit Secrets में GOOGLE_API_KEY नहीं है!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# AI को 'सीनियर डेवलपर' बनाने का निर्देश
SYSTEM_PROMPT = """
तुम दुनिया के सबसे बेहतरीन सॉफ्टवेयर आर्किटेक्ट और Python कोडर हो।
तुम्हें बिल्कुल Claude 3.5 Sonnet जैसी लॉजिकल और एरर-फ्री कोडिंग करनी है।
यूज़र PropertyHub नाम का एक नेशनल रियल एस्टेट प्लेटफ़ॉर्म बना रहा है। फालतू बातें मत करना, सीधा और सटीक कोड देना।
"""

# लेटेस्ट और सबसे पावरफुल मॉडल
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=SYSTEM_PROMPT
)

# 4. Session State (AI की याददाश्त)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# 5. स्क्रीन पर पुरानी बातचीत को व्यवस्थित तरीके से दिखाना
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. चैट इनपुट बॉक्स
if prompt := st.chat_input("Claude की तरह अपना कोडिंग का सवाल यहाँ पूछें..."):
    
    # यूज़र का सवाल स्क्रीन पर दिखाएं
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI का जवाब जनरेट करें
    with st.chat_message("assistant"):
        try:
            # लोडिंग इफ़ेक्ट के साथ जवाब लाना
            with st.spinner("Generating perfect code..."):
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"❌ सर्वर एरर: {e}")
            st.info("सुझाव: अगर फिर से एरर आए, तो साइडबार से 'New Chat' पर क्लिक करें।")
