import streamlit as st
import requests
import time
import re
import pandas as pd
import random
import threading
from datetime import datetime, timedelta

# --- 1. الإعدادات والمظهر الملكي ---
st.set_page_config(page_title="VOX ROYAL PRO", page_icon="👑", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f1f5f9; }
    .status-card {
        background: rgba(30, 41, 59, 0.7);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-val { font-size: 24px; font-weight: bold; color: #60a5fa; }
    .log-box { background: #000; color: #22c55e; padding: 10px; border-radius: 10px; font-family: 'Courier New'; height: 250px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الحالة (نظام التتبع السحابي) ---
if 'running' not in st.session_state: st.session_state.running = False
if 'sent_count' not in st.session_state: st.session_state.sent_count = 0
if 'total_count' not in st.session_state: st.session_state.total_count = 0
if 'logs' not in st.session_state: st.session_state.logs = []
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'estimated_end' not in st.session_state: st.session_state.estimated_end = ""

# بيانات Green API و Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"
ID_INSTANCE = "7107567423"
API_TOKEN = "bcb03e53bcde4e199d1a907abf87a42ba298303638044cfc81"

def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('0'): clean = '212' + clean[1:]
    return clean

# --- 3. محرك الإرسال الخلفي مع حساب الوقت ---
def background_worker(targets, audio_url, delay_val):
    st.session_state.running = True
    st.session_state.total_count = len(targets)
    st.session_state.sent_count = 0
    st.session_state.start_time = datetime.now()
    
    # حساب الوقت التقديري للنهاية
    total_seconds = st.session_state.total_count * (delay_val + 1)
    st.session_state.estimated_end = (datetime.now() + timedelta(seconds=total_seconds)).strftime("%H:%M:%S")

    for i, raw in enumerate(targets):
        num = sanitize(raw)
        endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
        payload = {"chatId": f"{num}@c.us", "urlFile": audio_url, "fileName": "audio.ogg"}
        
        try:
            res = requests.post(endpoint, json=payload, timeout=20)
            if res.status_code == 200:
                st.session_state.sent_count += 1
                st.session_state.logs.append(f"✅ [{datetime.now().strftime('%H:%M')}] تم الإرسال لـ {num}")
            else:
                st.session_state.logs.append(f"❌ خطأ في الرقم {num}")
        except:
            st.session_state.logs.append(f"⚠️ فشل الاتصال أثناء إرسال {num}")

        # انتظار أمان
        time.sleep(delay_val + random.uniform(0.1, 0.9))
            
    st.session_state.running = False
    st.session_state.logs.append("🏁 اكتملت جميع العمليات!")

# --- 4. واجهة التحكم ---
st.title("👑 VOX ROYAL PRO | Dashboard")

col_set, col_stats = st.columns([1, 2])

with col_set:
    st.markdown("### ⚙️ الإعدادات")
    try:
        df = pd.read_csv(SHEET_URL)
        audio_dict = dict(zip(df.iloc[:,0], df.iloc[:,1]))
        selected = st.selectbox("🎙️ التسجيل:", list(audio_dict.keys()))
        audio_url = audio_dict[selected]
    except:
        st.error("خطأ في رابط Sheets")
        audio_url = ""

    delay = st.number_input("⏲️ التأخير بين الرسائل (ثواني):", 2, 60, 5)
    numbers_raw = st.text_area("👥 الأرقام:", height=150)
    
    if st.button("🚀 بدء الإرسال في الخلفية"):
        if not st.session_state.running:
            targets = [n.strip() for n in numbers_raw.split('\n') if n.strip()]
            st.session_state.logs = []
            thread = threading.Thread(target=background_worker, args=(targets, audio_url, delay))
            thread.start()
            st.rerun()

with col_stats:
    st.markdown("### 📊 حالة الحملة الحالية")
    
    # مربعات الإحصائيات
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="status-card">تم الإرسال<br><span class="metric-val">{st.session_state.sent_count} / {st.session_state.total_count}</span></div>', unsafe_allow_html=True)
    with m2:
        rem = st.session_state.total_count - st.session_state.sent_count
        st.markdown(f'<div class="status-card">المتبقي<br><span class="metric-val">{rem}</span></div>', unsafe_allow_html=True)
    with m3:
        status_text = "🟢 يعمل" if st.session_state.running else "⚪ متوقف"
        st.markdown(f'<div class="status-card">الحالة<br><span class="metric-val">{status_text}</span></div>', unsafe_allow_html=True)

    if st.session_state.running:
        progress = st.session_state.sent_count / st.session_state.total_count
        st.progress(progress)
        st.warning(f"🕒 الوقت المتوقع للانتهاء: {st.session_state.estimated_end}")

    st.markdown("### 📜 سجل العمليات")
    log_html = "<br>".join(st.session_state.logs[::-1])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# تحديث تلقائي كل 3 ثوانٍ لمراقبة التقدم
if st.session_state.running:
    time.sleep(3)
    st.rerun()
