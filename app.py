import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AI Coder", page_icon="💻")
st.title("💻 Limitless AI Coding Assistant")

# API Key Check
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Secrets में GOOGLE_API_KEY सेट नहीं है!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Setup Model (Gemini 1.5 Flash - यह बेस्ट और स्टेबल है)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("अपना सवाल यहाँ लिखें..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
