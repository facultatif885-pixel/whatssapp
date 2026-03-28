import streamlit as st
import requests
import time
import re
import pandas as pd
import random

# --- 1. الإعدادات والمظهر الملكي ---
st.set_page_config(page_title="VOX ROYAL - 2CHAT PRO", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0f172a, #1e1b4b); color: #f1f5f9; }
    .stBlock { background: rgba(255, 255, 255, 0.03); padding: 25px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #4f46e5, #3730a3);
        color: white; border: none; border-radius: 12px; padding: 18px; font-weight: bold;
    }
    h1, h3 { color: #818cf8 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات التقنية (2Chat) ---
# تم وضع الـ API Key الخاص بك هنا مباشرة
API_KEY_2CHAT = "UAK14da7dba-aafb-465f-a665-01c2710aa463"
# ⚠️ هام: ضع رقم هاتفك المربوط بـ 2Chat هنا (بدون +)
SENDER_PHONE = "212XXXXXXXXX" 

API_ENDPOINT = "https://api.2chat.co/v1/messaging/send/audio"

# --- 3. جلب البيانات من Google Sheet ---
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

st.markdown("<h1>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البث الاحترافي المتصل بـ 2Chat</p>", unsafe_allow_html=True)
st.divider()

# --- 4. واجهة المستخدم ---
with st.container():
    st.markdown("### 🎙️ المكتبة السحابية")
    selected = st.selectbox("اختر التسجيل الصوتي:", list(audio_library.keys()))
    current_url = audio_library.get(selected, "")
    st.text_input("رابط الأوديو النشط:", value=current_url, disabled=True)
    
    st.markdown("### ⏲️ إعدادات الحماية")
    delay = st.slider("الانتظار (ثواني):", 10, 120, 20)

with st.expander("👥 إدارة الأرقام المستهدفة", expanded=True):
    numbers_input = st.text_area("أدخل الأرقام (تطهير تلقائي):", height=150)

# --- 5. محرك الإرسال ---
def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('0'): clean = '212' + clean[1:]
    return clean

if st.button("إطلاق الحملة الملكية 🚀"):
    if not current_url or not numbers_input:
        st.warning("⚠️ يرجى اختيار تسجيل وإدخال أرقام.")
    elif SENDER_PHONE == "212XXXXXXXXX":
        st.error("❌ خطأ: يرجى كتابة رقم هاتفك المرسل في الكود (SENDER_PHONE).")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(targets)
        progress = st.progress(0)
        status = st.empty()

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
                res = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=40)
                
                if res.status_code in [200, 201, 202]:
                    status.success(f"✅ [{index+1}/{total}] تم الإرسال للرقم: {num}")
                else:
                    # استخراج تفاصيل الخطأ من 2Chat
                    error_info = res.json().get('error', res.text)
                    status.error(f"❌ رفض من المنصة لـ {num}: {error_info}")
            
            except Exception as e:
                status.error(f"⚠️ خطأ غير متوقع: {str(e)}")

            progress.progress((index + 1) / total)
            if index < total - 1:
                time.sleep(delay + random.uniform(1, 4))

        st.balloons()
        st.success("✨ انتهت الحملة بنجاح!")
