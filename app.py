import streamlit as st
import google.generativeai as genai
import uuid, json, os, io
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr

# API Config
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ API Key नहीं मिली!")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 1. 🔍 सबसे लेटेस्ट और वर्किंग मॉडल ढूंढने का फंक्शन
@st.cache_resource
def get_best_model():
    # Google API से उन मॉडल्स की लिस्ट मांगें जो generateContent सपोर्ट करते हैं
    try:
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # कोशिश करें कि 1.5-flash या 1.5-pro मिल जाए, क्योंकि ये सबसे स्टेबल हैं
        for m in models:
            if 'gemini-1.5-flash' in m.name: return m.name
        for m in models:
            if 'gemini-1.5-pro' in m.name: return m.name
        return models[0].name # अगर कुछ न मिले तो पहला वर्किंग मॉडल ले लो
    except Exception as e:
        return 'gemini-1.5-flash' # बैकअप

# मॉडल को इनिशियलाइज़ करें
current_model_name = get_best_model()
model = genai.GenerativeModel(current_model_name)

# UI & Logic... (बाकी कोड वैसा ही रहेगा)
st.title("⚡ J.A.R.V.I.S. OMNI")
st.caption(f"Active Engine: {current_model_name}")

# ... (बाकी का चैट और वॉइस कोड यहाँ डालें)
