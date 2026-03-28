import streamlit as st
import requests
import time
import re
import pandas as pd
import random

# --- 1. الإعدادات والمظهر الملكي ---
st.set_page_config(page_title="VOX ROYAL PRO - 2CHAT", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0f172a, #1e1b4b); color: #f1f5f9; }
    .stBlock { background: rgba(255, 255, 255, 0.03); padding: 25px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background: rgba(0,0,0,0.3) !important; color: #818cf8 !important;
        border: 1px solid rgba(129, 140, 248, 0.2) !important;
    }
    div.stButton > button:first-child {
        width: 100%; background: linear-gradient(90deg, #4f46e5, #3730a3);
        color: white; border: none; border-radius: 12px; padding: 18px; font-weight: bold;
    }
    h1, h3 { color: #818cf8 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب البيانات من Google Sheet ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=10)
def load_audio_library():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        return dict(zip(df['name'], df['url']))
    except:
        return {"قائمة فارغة": ""}

audio_library = load_audio_library()

# --- 3. إعدادات 2CHAT (قم بتعبئتها) ---
# يمكنك وضع الـ API Key مباشرة هنا أو في Secrets
API_KEY_2CHAT = "UAK14da7dba-aafb-465f-a665-01c2710aa463" 
SENDER_PHONE = "212623738383" # رقم هاتفك المرتبط بـ 2Chat (بدون +)

st.markdown("<h1>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البث الذكي عبر منصة 2Chat</p>", unsafe_allow_html=True)
st.divider()

# --- 4. واجهة التحكم ---
with st.container():
    st.markdown("### 🎙️ المكتبة السحابية")
    names = list(audio_library.keys())
    selected = st.selectbox("اختر التسجيل من جدول Google:", names)
    current_url = audio_library.get(selected, "")
    
    st.markdown("### ⏲️ إعدادات الحماية")
    delay = st.slider("الانتظار بين الرسائل (ثواني):", 5, 120, 20)

with st.expander("👥 إدارة الأرقام المستهدفة", expanded=True):
    numbers_input = st.text_area("أدخل الأرقام هنا:", height=150)

# --- 5. محرك الإرسال (2Chat API) ---
def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('00212'): clean = clean[2:]
    elif clean.startswith('0'): clean = '212' + clean[1:]
    elif len(clean) == 9: clean = '212' + clean
    return clean

if st.button("إطلاق الحملة عبر 2CHAT ⚡"):
    if not current_url or not numbers_input or API_KEY_2CHAT == "وضـع_API_KEY_الخاص_بك_هنا":
        st.warning("⚠️ تأكد من إدخال الـ API Key واختيار تسجيل وأرقام.")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(targets)
        progress = st.progress(0)
        status = st.empty()

        # إعداد رأس الطلب (Headers) لـ 2Chat
        headers = {
            "X-User-API-Key": API_KEY_2CHAT,
            "Content-Type": "application/json"
        }

        for index, raw in enumerate(targets):
            num = sanitize(raw)
            if not num: continue

            # عنوان الإرسال في 2Chat
            endpoint = "https://api.2chat.co/v1/messaging/send/audio"
            
            payload = {
                "to_number": f"+{num}", # 2Chat يفضل وجود علامة +
                "from_number": f"+{SENDER_PHONE}",
                "audio_url": current_url
            }

            try:
                res = requests.post(endpoint, json=payload, headers=headers, timeout=30)
                if res.status_code in [200, 201, 202]:
                    status.success(f"✅ [{index+1}/{total}] تم الإرسال لـ: {num}")
                else:
                    err = res.json().get('error', 'خطأ في المنصة')
                    status.error(f"❌ فشل مع {num}: {err}")
            except Exception as e:
                status.error(f"❌ خطأ تقني: {str(e)}")

            progress.progress((index + 1) / total)
            if index < total - 1:
                time.sleep(delay + random.uniform(1, 3))

        st.balloons()
        st.success("✨ انتهت الحملة!")

st.markdown("<p style='text-align: center; color: rgba(148,163,184,0.3); font-size: 10px; margin-top: 30px;'>VOX ROYAL PRO • POWERED BY 2CHAT • 2026</p>", unsafe_allow_html=True)
