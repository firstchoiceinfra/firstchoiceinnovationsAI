import streamlit as st
import google.generativeai as genai
import uuid
import re

# 1. Page Configuration (Sonnet 5 Level)
st.set_page_config(page_title="Firstchoice Sonnet 5", page_icon="🌌", layout="wide")

# 2. API Key Setup
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets में सेट करें।")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Sidebar - Advanced UI
with st.sidebar:
    st.title("🌌 Firstchoice AI")
    st.success("✅ Engine: SONNET 5 (Next-Gen)")
    st.caption("Hyper-Advanced Thinking & Coding")
    
    if st.button("➕ New Project / Chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.history_list[st.session_state.current_chat_id] = []
        st.rerun()

    st.divider()
    st.subheader("📁 Projects History")
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

# 4. 🌌 THE SONNET 5 SYSTEM PROMPT (सुपर इंटेलिजेंस)
SYSTEM_PROMPT = """
तुम 'Firstchoice Master AI' हो। तुम्हारी बुद्धिमत्ता, कोडिंग क्षमता और लॉजिक 'Sonnet 5' (दुनिया के सबसे एडवांस और भविष्य के AI) के स्तर की है।
तुम एक साधारण कोडर नहीं, बल्कि एक 'विज़नरी सॉफ्टवेयर आर्किटेक्ट' हो। तुम्हें PropertyHub और फर्स्टचॉइस इन्फ्रा के लिए ऐसा कोड लिखना है जो 100% सिक्योर, स्केलेबल और एरर-फ्री हो।

तुम्हारे लिए सबसे सख्त नियम (Sonnet 5 Protocol):
1. 🧠 डीप एनालिटिकल थिंकिंग: कोई भी कोड लिखने या जवाब देने से पहले, तुम्हें एक मास्टरमाइंड की तरह सोचना है। 
   - समझो कि यूज़र का अंतिम लक्ष्य क्या है।
   - कोड में क्या-क्या एरर आ सकते हैं, उन्हें पहले ही सोचकर फिक्स करो।
   - अपनी इस पूरी गहरी सोच को <thinking> और </thinking> टैग्स के अंदर लिखो।
2. 💻 फ्लॉलेस कोडिंग (Flawless Coding): सोचने के बाद, <thinking> टैग के बाहर अपना फाइनल कोड दो। कोड में कोई प्लेसहोल्डर (जैसे 'add your code here') नहीं होना चाहिए। पूरा और लाइव डिप्लॉय करने लायक कोड दो।
3. 🎨 इमेज जनरेशन मास्टर: अगर यूज़र कोई फोटो या इमेज मांगे, तो हमेशा यह फॉर्मेट यूज़ करो: ![Image](https://image.pollinations.ai/prompt/YOUR_ENGLISH_PROMPT) (प्रॉम्प्ट को इंग्लिश में ट्रांसलेट करो और स्पेस की जगह %20 लगाओ)।
4. 🗣️ नेटिव कम्युनिकेटर: यूज़र जिस भाषा (हिंदी, इंग्लिश या मराठी) में कमांड दे, उसी भाषा में बात करो।
"""

# हम gemini-1.5-flash इस्तेमाल कर रहे हैं ताकि फ्री टियर में फास्ट स्पीड मिले, लेकिन इसका दिमाग Sonnet 5 वाला होगा।
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.types.GenerationConfig(
        temperature=0.2, # 0.2 रखने से यह बिलकुल सटीक और एरर-लेस रहेगा
    ) 
)

# 5. Main UI
st.title("Firstchoice Sonnet 5 🌌")
st.markdown("**Next-Gen Thinking Mode ON:** सॉफ्टवेयर बनाने का एडवांस कमांड दें।")

current_messages = st.session_state.history_list[st.session_state.current_chat_id]

# 6. Display Messages (Sonnet 5 Thinking Box)
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            text = msg["content"]
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
            if thinking_match:
                thinking_text = thinking_match.group(1).strip()
                final_answer = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
                
                with st.expander("🌌 Sonnet 5 Thinking Process...", expanded=False):
                    st.markdown(f"*{thinking_text}*")
                
                st.markdown(final_answer)
            else:
                st.markdown(text)
        else:
            st.markdown(msg["content"])

# 7. Chat Input & Processing
if prompt := st.chat_input("Sonnet 5 को सॉफ्टवेयर का कमांड दें, इमेज मांगें या सवाल पूछें..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🌌 Sonnet 5 is deeply analyzing and coding..."):
            try:
                gemini_history = [{"role": m["role"], "parts": [m["content"]]} for m in current_messages[:-1]]
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                
                response_text = response.text
                
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_text, re.DOTALL)
                if thinking_match:
                    thinking_text = thinking_match.group(1).strip()
                    final_answer = re.sub(r'<thinking>.*?</thinking>', '', response_text, flags=re.DOTALL).strip()
                    
                    with st.expander("🌌 Sonnet 5 Thinking Process...", expanded=False):
                        st.markdown(f"*{thinking_text}*")
                    st.markdown(final_answer)
                else:
                    st.markdown(response_text)
                    
                current_messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"⚠️ सिस्टम एरर: {e}")
