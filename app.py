import streamlit as st
import requests
import time
import re
import pandas as pd
import random

# --- الإعدادات ---
st.set_page_config(page_title="VOX ROYAL - 2CHAT", page_icon="👑")

# --- روابط 2Chat المحدثة ---
# جرب هذا الرابط أولاً، إذا لم يعمل استبدله بـ api.2chat.co
API_BASE_URL = "https://api.p2chat.io/v1/messaging/send/audio"

# --- البيانات (تأكد من ملئها) ---
API_KEY_2CHAT = "UAK14da7dba-aafb-465f-a665-01c2710aa463" 
SENDER_PHONE = "212623738383" 

# --- جلب البيانات من Google Sheet ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=10)
def load_audio_library():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        return dict(zip(df['name'], df['url']))
    except:
        return {"خطأ في الجدول": ""}

audio_library = load_audio_library()

st.title("👑 VOX ROYAL PRO - 2CHAT")

# --- واجهة التحكم ---
selected = st.selectbox("اختر التسجيل:", list(audio_library.keys()))
current_url = audio_library.get(selected, "")
delay = st.slider("الانتظار (ثواني):", 10, 120, 20)
numbers_input = st.text_area("الأرقام:")

def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('0'): clean = '212' + clean[1:]
    return clean

if st.button("إطلاق الحملة 🚀"):
    targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
    headers = {
        "X-User-API-Key": API_KEY_2CHAT,
        "Content-Type": "application/json"
    }

    for index, raw in enumerate(targets):
        num = sanitize(raw)
        # 2Chat يتطلب الرقم مع علامة +
        payload = {
            "to_number": f"+{num}",
            "from_number": f"+{SENDER_PHONE}",
            "audio_url": current_url
        }

        try:
            # استخدام الرابط المحدث
            res = requests.post(API_BASE_URL, json=payload, headers=headers, timeout=30)
            if res.status_code in [200, 201, 202]:
                st.success(f"✅ تم الإرسال لـ: {num}")
            else:
                st.error(f"❌ فشل: {res.text}")
        except Exception as e:
            st.error(f"⚠️ مشكلة في الاتصال بالخادم: {str(e)}")
            st.info("نصيحة: تأكد من كتابة الرابط الصحيح في إعدادات 2Chat")

        if index < len(targets) - 1:
            time.sleep(delay)
