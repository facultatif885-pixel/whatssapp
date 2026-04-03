import streamlit as st
import requests
import time
import re
import pandas as pd
import random
import threading

# --- 1. الإعدادات والمظهر الملكي ---
st.set_page_config(page_title="VOX ROYAL PRO", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; }
    .stBlock { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(0,0,0,0.4) !important; color: #60a5fa !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important; border-radius: 12px !important;
    }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white; border: none; border-radius: 12px; padding: 18px; font-weight: bold;
    }
    h1, h2, h3 { color: #60a5fa !important; }
    .log-box { background: #000; color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace; height: 200px; overflow-y: scroll; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الحالة (Session State) لضمان الاستمرار ---
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

# رابط Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"
ID_INSTANCE = "7107567423"
API_TOKEN = "bcb03e53bcde4e199d1a907abf87a42ba298303638044cfc81"

@st.cache_data(ttl=10)
def load_audio_library():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        return dict(zip(df['name'], df['url']))
    except:
        return {"قائمة فارغة": ""}

def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('00212'): clean = clean[2:]
    elif clean.startswith('0'): clean = '212' + clean[1:]
    elif len(clean) == 9: clean = '212' + clean
    return clean

# --- 3. محرك الإرسال في الخلفية ---
def background_sender(targets, audio_url, delay_val):
    st.session_state.is_running = True
    total = len(targets)
    
    for i, raw in enumerate(targets):
        num = sanitize(raw)
        endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
        payload = {
            "chatId": f"{num}@c.us",
            "urlFile": audio_url,
            "fileName": "royal_audio.ogg"
        }
        
        try:
            res = requests.post(endpoint, json=payload, timeout=20)
            if res.status_code == 200:
                st.session_state.logs.append(f"✅ {i+1}/{total} - تم الإرسال لـ {num}")
            else:
                st.session_state.logs.append(f"❌ {i+1}/{total} - فشل للرقم {num}")
        except Exception as e:
            st.session_state.logs.append(f"⚠️ خطأ فني مع الرقم {num}")

        if i < total - 1:
            time.sleep(delay_val + random.uniform(0.5, 1.5))
            
    st.session_state.is_running = False
    st.session_state.logs.append("✨ تمت المهمة بنجاح!")

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center;'>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    audio_library = load_audio_library()
    selected = st.selectbox("🎙️ اختر التسجيل:", list(audio_library.keys()))
    current_url = audio_library.get(selected, "")
    delay = st.slider("⏲️ الانتظار (ثواني):", 2, 60, 5)

with col2:
    numbers_input = st.text_area("👥 قائمة الأرقام:", height=150)

if st.button("🚀 إطلاق الحملة في الخلفية"):
    if st.session_state.is_running:
        st.error("⚠️ هناك حملة تعمل بالفعل حالياً!")
    elif not current_url or not numbers_input:
        st.warning("⚠️ تأكد من الأرقام والروابط!")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        st.session_state.logs = [] # تصفير السجل القديم
        
        # بدء الخيط (Thread)
        t = threading.Thread(target=background_sender, args=(targets, current_url, delay))
        t.start()
        st.info("🔄 بدأت المعالجة.. يمكنك إغلاق المتصفح الآن.")

# --- 5. عرض سجل العمليات المباشر ---
st.markdown("### 📊 سجل العمليات المباشر")
log_container = st.empty()
log_content = "\n".join(st.session_state.logs[::-1]) # عرض الأحدث أولاً
log_container.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)

# تحديث تلقائي للواجهة إذا كانت الحملة تعمل
if st.session_state.is_running:
    time.sleep(2)
    st.rerun()

st.markdown("<p style='text-align: center; color: gray; font-size: 10px;'>VOX ROYAL PRO • 2026</p>", unsafe_allow_html=True)
