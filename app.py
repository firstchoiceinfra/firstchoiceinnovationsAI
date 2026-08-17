import streamlit as st
import google.generativeai as genai
import uuid

# 1. Page Config
st.set_page_config(page_title="Firstchoice AI", page_icon="⚡", layout="wide")

# 2. Setup API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("API Key नहीं मिली!")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Sidebar: History Management
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    
    # 'New Chat' बटन
    if st.button("➕ New Chat"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📜 Chat History")
    
    # हिस्ट्री को मैनेज करना (डिलिट करना)
    if "history_list" not in st.session_state:
        st.session_state.history_list = {}
    
    # चैट लिस्ट दिखाना
    for chat_id, messages in list(st.session_state.history_list.items()):
        col1, col2 = st.columns([0.8, 0.2])
        if col1.button(f"Chat {chat_id[:4]}", key=f"btn_{chat_id}"):
            st.session_state.current_chat_id = chat_id
        if col2.button("🗑️", key=f"del_{chat_id}"):
            del st.session_state.history_list[chat_id]
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = None
            st.rerun()

# 4. Initialize State
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []

# 5. AI Model
model = genai.GenerativeModel('gemini-1.5-pro')

# 6. Chat Display
st.title("कोडिंग असिस्टेंट")
current_messages = st.session_state.history_list[st.session_state.current_chat_id]

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Chat Input
if prompt := st.chat_input("अपना सवाल लिखें..."):
    # User message
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI message
    with st.chat_message("assistant"):
        with st.spinner("Generating..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
            st.rerun()
