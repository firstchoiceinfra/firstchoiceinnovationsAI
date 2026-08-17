import streamlit as st
import google.generativeai as genai
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Firstchoice AI Coder", page_icon="⚡", layout="wide")

# 2. API Key Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में 'GOOGLE_API_KEY' सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Sidebar - History Management & UI
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    st.success("✅ Connected: Gemini 1.5 Flash (Limit-Free)")
    st.caption("Multilingual Software Engineering Edition")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📜 Chat History")
    
    if "history_list" not in st.session_state:
        st.session_state.history_list = {}
    
    # Display and manage chat history
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

# 4. Initialize Chat Session State
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []

# 5. Setup AI Model (Using gemini-1.5-flash to avoid 429 Quota errors)
SYSTEM_PROMPT = """
तुम दुनिया के सबसे बेहतरीन सीनियर सॉफ्टवेयर इंजीनियर और आर्किटेक्ट हो।
तुम्हारी विशेषज्ञता Python, Streamlit, डेटाबेस मैनेजमेंट और सुरक्षित वेब डेवलपमेंट में है।
तुम्हें PropertyHub जैसे नेशनल रियल एस्टेट और वेंडर सर्विस प्लेटफ़ॉर्म को बनाने के लिए सटीक, ऑप्टिमाइज़्ड और बिल्कुल एरर-फ्री कोड देना है।

सख्त नियम:
1. कोड बिल्कुल साफ (Clean), मॉड्यूलर और कमेंट्स के साथ होना चाहिए।
2. कोई भी अधूरा कोड मत देना, पूरा काम करने वाला कोड ही जनरेट करना।
3. जिस भाषा (हिंदी, मराठी या इंग्लिश) में सवाल पूछा जाए, उसी भाषा में जवाब देना और कोड समझाना।
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(temperature=0.2)
)

# 6. Main Chat UI
st.title("Firstchoice Coder 💻")
st.markdown("हिंदी, मराठी या English में कोडिंग से जुड़ा कोई भी सवाल पूछें।")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

# Display previous messages
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Chat Input & Response Generation
if prompt := st.chat_input("सॉफ्टवेयर बनाने के लिए अपना सवाल यहाँ लिखें..."):
    # Add user message to UI and history
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Generating Error-Free Code..."):
            try:
                # Convert history to Gemini format
                gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                chat_session = model.start_chat(history=gemini_history)
                
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                current_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ एरर: {e}")
                st.info("सुझाव: अगर एरर आए तो साइडबार से 'New Chat' पर क्लिक करें।")
