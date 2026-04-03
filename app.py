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
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background: rgba(0,0,0,0.4) !important; color: #60a5fa !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important; border-radius: 12px !important;
    }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white; border: none; border-radius: 12px; padding: 18px; font-weight: bold;
    }
    h1, h2, h3 { color: #60a5fa !important; }
    .log-box { background: #000; color: #22c55e; padding: 10px; border-radius: 10px; font-family: monospace; height: 150px; overflow-y: auto; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الحالة (لحفظ البيانات عند الريفريش) ---
if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'progress' not in st.session_state: st.session_state.progress = 0.0
if 'current_target' not in st.session_state: st.session_state.current_target = ""

# البيانات الثابتة
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

# --- 3. محرك الإرسال الخلفي (Worker) ---
def background_campaign(targets, audio_url, delay_val):
    st.session_state.is_running = True
    total = len(targets)
    
    for index, raw in enumerate(targets):
        num = sanitize(raw)
        st.session_state.current_target = f"جاري الإرسال لـ: {num} ({index+1}/{total})"
        
        endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
        payload = {
            "chatId": f"{num}@c.us", 
            "urlFile": audio_url, 
            "fileName": "royal_audio.ogg"
        }
        
        try:
            res = requests.post(endpoint, json=payload, timeout=25)
            if res.status_code == 200:
                st.session_state.logs.append(f"✅ تم بنجاح: {num}")
            else:
                st.session_state.logs.append(f"❌ فشل: {num} (كود {res.status_code})")
        except:
            st.session_state.logs.append(f"⚠️ خطأ اتصال: {num}")
        
        # تحديث التقدم
        st.session_state.progress = (index + 1) / total
        
        # نظام الانتظار
        if index < total - 1:
            time.sleep(delay_val + random.uniform(0.5, 1.5))

    st.session_state.is_running = False
    st.session_state.logs.append("✨ اكتملت المهمة بنجاح!")

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center;'>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.divider()

audio_library = load_audio_library()
names = list(audio_library.keys())
selected = st.selectbox("اختر التسجيل:", names)
current_url = audio_library.get(selected, "")

delay = st.slider("الانتظار بين الرسائل (ثواني):", 2, 60, 5)
numbers_input = st.text_area("أدخل الأرقام:", height=150)

if st.button("تطهير وإطلاق الحملة في الخلفية ⚡"):
    if st.session_state.is_running:
        st.warning("⚠️ هناك حملة تعمل بالفعل في الخلفية!")
    elif not current_url or not numbers_input:
        st.error("⚠️ يرجى التأكد من البيانات.")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        st.session_state.logs = []
        st.session_state.progress = 0.0
        
        # تشغيل المحرك في خيط (Thread) منفصل
        thread = threading.Thread(target=background_campaign, args=(targets, current_url, delay))
        thread.start()
        st.info("🔄 بدأت الحملة! يمكنك إغلاق الصفحة أو عمل ريفريش، سأستمر في العمل.")

# --- 5. لوحة المراقبة (تظهر دائماً وتحدث نفسها) ---
if st.session_state.is_running or st.session_state.progress > 0:
    st.divider()
    st.markdown(f"### 📊 حالة الحملة: {'🟢 نشطة' if st.session_state.is_running else '⚪ منتهية'}")
    st.progress(st.session_state.progress)
    st.write(st.session_state.current_target)
    
    with st.expander("📄 سجل العمليات التفصيلي", expanded=True):
        log_text = "\n".join(st.session_state.logs[::-1])
        st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)

    # تحديث تلقائي للواجهة كل ثانيتين لترى النتائج
    if st.session_state.is_running:
        time.sleep(2)
        st.rerun()

st.markdown("<p style='text-align: center; color: gray; font-size: 10px;'>VOX ROYAL PRO • 2026</p>", unsafe_allow_html=True)
