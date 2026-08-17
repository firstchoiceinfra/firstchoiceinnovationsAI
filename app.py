import streamlit as st
import google.generativeai as genai
import uuid

# 1. Page Config
st.set_page_config(page_title="Firstchoice AI Coder", page_icon="⚡", layout="wide")

# 2. API Key Check
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. ब्रह्मास्त्र: ऑटोमैटिक उपलब्ध मॉडल खोजना (Auto-Detect Model)
@st.cache_resource
def get_working_model():
    try:
        available_models = []
        # यह लाइन खुद Google से उपलब्ध मॉडल्स की लिस्ट मांगेगी
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name.replace('models/', ''))
        
        if not available_models:
            return "NO_MODELS_FOUND"
            
        # सबसे बेस्ट मॉडल को प्राथमिकता देना
        for m in available_models:
            if '1.5-flash' in m: return m
        for m in available_models:
            if '1.5-pro' in m: return m
        for m in available_models:
            if 'pro' in m: return m
            
        return available_models[0] # जो भी पहला मिले उसे ले लो
    except Exception as e:
        return f"ERROR: {e}"

actual_model_name = get_working_model()

# अगर API Key में कोई मॉडल न हो
if actual_model_name == "NO_MODELS_FOUND":
    st.error("❌ आपकी API Key में कोई भी AI मॉडल उपलब्ध नहीं है। कृपया Google AI Studio से एक नई (Fresh) API Key जनरेट करें।")
    st.stop()
elif actual_model_name.startswith("ERROR"):
    st.error(f"❌ API से कनेक्ट करने में समस्या: {actual_model_name}")
    st.stop()

# 4. Sidebar & History Management
with st.sidebar:
    st.title("⚡ Firstchoice AI")
    # यहाँ आपको हरे रंग में दिखेगा कि कौन सा मॉडल कनेक्ट हुआ है
    st.success(f"✅ Connected: {actual_model_name}")
    st.caption("Expert Software Engineering Edition")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📜 Chat History")
    
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

# 5. Initialize State
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id is None:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.history_list[st.session_state.current_chat_id] = []

# 6. Model Setup
SYSTEM_PROMPT = """
तुम दुनिया के सबसे बेहतरीन सीनियर सॉफ्टवेयर इंजीनियर और आर्किटेक्ट हो।
तुम्हें PropertyHub जैसे नेशनल रियल एस्टेट और वेंडर सर्विस प्लेटफ़ॉर्म को बनाने के लिए सटीक, ऑप्टिमाइज़्ड और बिल्कुल एरर-फ्री कोड देना है।
तुम यूज़र के सवालों का जवाब हिंदी, इंग्लिश या मराठी (जिसमें पूछा जाए) में दोगे।
"""

model = genai.GenerativeModel(
    model_name=actual_model_name,
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(temperature=0.2)
)

# 7. Chat Display
st.title("Firstchoice Coder 💻")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Chat Input
if prompt := st.chat_input("सॉफ्टवेयर बनाने के लिए अपना सवाल या प्रॉम्प्ट यहाँ लिखें..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Generating Code using {actual_model_name}..."):
            try:
                gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                current_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ एरर: {e}")
