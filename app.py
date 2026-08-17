import streamlit as st
import google.generativeai as genai
import uuid

# 1. Page Config
st.set_page_config(page_title="Firstchoice AI Coder", page_icon="⚡", layout="wide")

# 2. Setup API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Sidebar: History Management
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    st.success("✅ Connected: gemini-1.5-flash")
    st.caption("Expert Software Engineering Edition")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📜 Chat History")
    
    if "history_list" not in st.session_state:
        st.session_state.history_list = {}
    
    # चैट लिस्ट दिखाना और डिलीट करने का ऑप्शन
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

# 4. Initialize State
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []

# 5. Expert Coding System Prompt & NEW MODEL Setup
SYSTEM_PROMPT = """
तुम दुनिया के सबसे बेहतरीन सीनियर सॉफ्टवेयर इंजीनियर और आर्किटेक्ट हो।
तुम्हारी विशेषज्ञता Python, Streamlit, डेटाबेस मैनेजमेंट और सुरक्षित वेब डेवलपमेंट में है।
तुम्हें PropertyHub जैसे नेशनल रियल एस्टेट और वेंडर सर्विस प्लेटफ़ॉर्म को बनाने के लिए सटीक, ऑप्टिमाइज़्ड और बिल्कुल एरर-फ्री कोड देना है।

तुम्हारे लिए सख्त नियम:
1. कोड बिल्कुल साफ (Clean), मॉड्यूलर और कमेंट्स के साथ होना चाहिए।
2. कोई भी अधूरा कोड मत देना, पूरा काम करने वाला कोड ही जनरेट करना।
3. जिस भाषा (हिंदी, मराठी या इंग्लिश) में सवाल पूछा जाए, उसी भाषा में कोड का लॉजिक समझाना।
4. बेस्ट प्रैक्टिसेस और डेटा सिक्योरिटी का पूरा ध्यान रखना।
"""

# यहाँ हमने वही नाम डाला है जो एरर ने हमें इस्तेमाल करने को कहा है
model = genai.GenerativeModel(
    model_name='gemini-3.1-pro-preview',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(temperature=0.2)
)

# 6. Chat Display
st.title("Firstchoice Coder 💻")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Chat Input
if prompt := st.chat_input("सॉफ्टवेयर बनाने के लिए अपना सवाल या प्रॉम्प्ट यहाँ लिखें..."):
    # User message
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI message - Chat session
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and Generating Error-Free Code..."):
            try:
                gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                current_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ एरर: {e}")
                st.info("कृपया साइडबार से 'New Chat' पर क्लिक करके दोबारा प्रयास करें।")
