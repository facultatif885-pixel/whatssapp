import streamlit as st
import requests
import time
import re
import pandas as pd
import random

# --- الإعدادات ---
st.set_page_config(page_title="VOX ROYAL - 2CHAT", page_icon="👑")

# الرابط الرسمي الصحيح لـ 2Chat
API_ENDPOINT = "https://api.2chat.co/v1/messaging/send/audio"

# --- البيانات (قم بتغييرها يدوياً هنا) ---
API_KEY_2CHAT = "UAK14da7dba-aafb-465f-a665-01c2710aa463" 
SENDER_PHONE = "212623738383" # رقمك المربوط في 2Chat بدون +

# --- جلب البيانات من Google Sheet ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        return dict(zip(df['name'], df['url']))
    except:
        return {"خطأ": "تعذر قراءة الجدول"}

audio_library = load_data()

st.markdown("### 👑 VOX ROYAL PRO (2CHAT Edition)")

# --- واجهة المستخدم ---
selected = st.selectbox("اختر التسجيل:", list(audio_library.keys()))
current_url = audio_library.get(selected, "")
delay = st.slider("الانتظار (ثواني):", 10, 120, 20)
numbers_input = st.text_area("أدخل الأرقام هنا:")

def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('0'): clean = '212' + clean[1:]
    return clean

if st.button("إرسال الآن 🚀"):
    if API_KEY_2CHAT == "UAK14da7dba-aafb-465f-a665-01c2710aa463":
        st.error("❌ خطأ: لم تقم بوضع API KEY الخاص بـ 2Chat في الكود!")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        headers = {
            "X-User-API-Key": API_KEY_2CHAT,
            "Content-Type": "application/json"
        }

        for index, raw in enumerate(targets):
            num = sanitize(raw)
            payload = {
                "to_number": f"+{num}",
                "from_number": f"+{SENDER_PHONE}",
                "audio_url": current_url
            }

            try:
                # محاولة الإرسال مع مهلة أطول (Timeout)
                res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=40)
                
                if res.status_code in [200, 201, 202]:
                    st.success(f"✅ تم الإرسال للرقم: {num}")
                else:
                    st.error(f"❌ رفض من 2Chat: {res.text}")
            
            except requests.exceptions.ConnectionError:
                st.error("⚠️ فشل الاتصال بخوادم 2Chat. تأكد من أن الموقع يعمل أو جرب Reboot للتطبيق.")
            except Exception as e:
                st.error(f"⚠️ خطأ غير متوقع: {str(e)}")

            if index < len(targets) - 1:
                time.sleep(delay + random.uniform(1, 3))

        st.balloons()
