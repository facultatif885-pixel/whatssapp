import streamlit as st
import requests
import time
import re
import pandas as pd
import random

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب البيانات من Google Sheet مباشرة عبر الرابط ---
# رابط الجدول الخاص بك بصيغة CSV لسهولة القراءة
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=10) # تحديث البيانات كل 10 ثواني
def load_audio_library():
    try:
        df = pd.read_csv(SHEET_URL)
        # التأكد من تنظيف أسماء الأعمدة (حذف المسافات)
        df.columns = df.columns.str.strip().str.lower()
        return dict(zip(df['name'], df['url']))
    except Exception as e:
        st.error("⚠️ لم يتمكن النظام من قراءة الجدول. تأكد أن العناوين في أول سطر هي name و url.")
        return {"قائمة فارغة": ""}

audio_library = load_audio_library()

# بيانات Green API الثابتة
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.markdown("<h1 style='text-align: center;'>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البث الملكي المتصل سحابياً</p>", unsafe_allow_html=True)
st.divider()

# --- 3. واجهة التحكم ---
with st.container():
    st.markdown("### 🎙️ المكتبة السحابية المباشرة")
    
    names = list(audio_library.keys())
    selected = st.selectbox("اختر التسجيل من جدول Google الخاص بك:", names)
    
    current_url = audio_library.get(selected, "")
    st.text_input("الرابط المعتمد حالياً:", value=current_url, disabled=True)
    
    st.markdown("### ⏲️ إعدادات الحماية (Anti-Ban)")
    delay = st.slider("الانتظار بين الرسائل (ثواني):", 2, 60, 5)

with st.expander("👥 إدارة الأرقام المستهدفة", expanded=True):
    numbers_input = st.text_area("أدخل الأرقام (تطهير تلقائي)", height=150, placeholder="06XXXXXXXX\n+2126XXXXXXX\n002126XXXXXXX")

# --- 4. محرك المعالجة والإرسال ---
def sanitize(phone):
    clean = re.sub(r'\D', '', str(phone)) # حذف كل ما ليس رقماً
    if clean.startswith('00212'): clean = clean[2:]
    elif clean.startswith('0'): clean = '212' + clean[1:]
    elif len(clean) == 9: clean = '212' + clean
    return clean

if st.button("تطهير الأرقام وإطلاق الحملة ⚡"):
    if not current_url or not numbers_input:
        st.warning("⚠️ يرجى التأكد من وجود روابط في الجدول وإدخال أرقام هواتف.")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(targets)
        
        progress = st.progress(0)
        status = st.empty()
        
        for index, raw in enumerate(targets):
            num = sanitize(raw)
            endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            payload = {
                "chatId": f"{num}@c.us", 
                "urlFile": current_url, 
                "fileName": "royal_audio.ogg"
            }
            
            try:
                res = requests.post(endpoint, json=payload, timeout=25)
                if res.status_code == 200:
                    status.success(f"✅ [{index+1}/{total}] تم الإرسال للهدف: {num}")
                else:
                    status.error(f"❌ فشل الإرسال للرقم: {num}")
            except:
                status.error(f"❌ خطأ في الاتصال بالشبكة")
            
            progress.progress((index + 1) / total)
            
            # نظام الانتظار للحماية
            if index < total - 1:
                # إضافة عشوائية بسيطة لزيادة الأمان
                actual_wait = delay + random.uniform(0.5, 1.5)
                time.sleep(actual_wait)

        st.balloons()
        st.success(f"✨ اكتملت المهمة بنجاح لـ {total} هدف!")

st.markdown("<p style='text-align: center; color: rgba(148,163,184,0.3); font-size: 10px; margin-top: 30px;'>VOX ROYAL PRO • CLOUD CONNECTED • 2026</p>", unsafe_allow_html=True)
