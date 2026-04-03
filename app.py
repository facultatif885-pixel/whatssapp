import streamlit as st
import requests
import time
import re
import pandas as pd
import random
import threading

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="VOX ROYAL PRO", page_icon="👑", layout="centered")

# تأكد من تعريف متغيرات الحالة لكي لا تضيع عند الريفريش
if 'sending_active' not in st.session_state:
    st.session_state.sending_active = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"
ID_INSTANCE = "7107567423"
API_TOKEN = "bcb03e53bcde4e199d1a907abf87a42ba298303638044cfc81"

# --- 2. وظائف المعالجة ---
def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('0'): clean = '212' + clean[1:]
    return clean

def run_campaign(targets, audio_url, delay_val):
    """هذه الوظيفة تعمل في الخلفية تماماً"""
    st.session_state.sending_active = True
    total = len(targets)
    
    for i in range(st.session_state.current_index, total):
        # تحديث المؤشر الحالي لكي نعرف أين توقفنا
        st.session_state.current_index = i
        num = sanitize(targets[i])
        
        endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
        payload = {
            "chatId": f"{num}@c.us",
            "urlFile": audio_url,
            "fileName": "audio.ogg"
        }
        
        try:
            res = requests.post(endpoint, json=payload, timeout=30)
            if res.status_code == 200:
                st.session_state.logs.append(f"✅ {i+1}/{total} - تم الإرسال لـ {num}")
            else:
                st.session_state.logs.append(f"❌ فشل في الرقم {num}")
        except:
            st.session_state.logs.append(f"⚠️ خطأ اتصال مع {num}")

        # وقت الانتظار
        time.sleep(delay_val + random.uniform(0.5, 1.5))
    
    st.session_state.sending_active = False
    st.session_state.current_index = 0 # إعادة التصفير عند الانتهاء التام

# --- 3. الواجهة الرسومية ---
st.title("👑 VOX ROYAL PRO")

# جلب البيانات من Google Sheet
try:
    df = pd.read_csv(SHEET_URL)
    audio_dict = dict(zip(df.iloc[:,0], df.iloc[:,1]))
    selected_audio = st.selectbox("اختر ملف الصوت:", list(audio_dict.keys()))
    current_url = audio_dict[selected_audio]
except:
    st.error("فشل في جلب بيانات الجدول")
    current_url = ""

numbers_input = st.text_area("أدخل قائمة الأرقام هنا:", height=150)
delay = st.slider("التأخير (ثواني):", 2, 60, 5)

if st.button("🚀 إطلاق الحملة المستمرة"):
    if not st.session_state.sending_active:
        targets_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        if targets_list and current_url:
            # بدء العملية في خيط منفصل (Thread)
            t = threading.Thread(target=run_campaign, args=(targets_list, current_url, delay))
            t.start()
            st.success("تم تشغيل الحملة في الخلفية! لا تغلق السيرفر.")
        else:
            st.warning("تأكد من إدخال الأرقام والروابط")
    else:
        st.info("الحملة تعمل بالفعل حالياً...")

# --- 4. عرض البيانات المباشرة (حتى بعد الريفريش) ---
st.divider()
st.subheader("📊 مراقبة الإرسال")

col1, col2 = st.columns(2)
with col1:
    st.metric("تم إرسال", f"{st.session_state.current_index} رسائل")
with col2:
    status = "🟢 يعمل حالياً" if st.session_state.sending_active else "⚪ متوقف"
    st.write(f"الحالة: **{status}**")

# عرض سجل العمليات الأخير
with st.expander("عرض السجل التفصيلي (Logs)"):
    for log in reversed(st.session_state.logs):
        st.write(log)

# كود التحديث التلقائي للواجهة
if st.session_state.sending_active:
    time.sleep(2)
    st.rerun()
