import streamlit as st
import requests
import time
import re
import pandas as pd
import random

# --- 1. الإعدادات البصرية (المظهر الملكي) ---
st.set_page_config(
    page_title="VOX ROYAL PRO",
    page_icon="👑",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1e3a8a, #0f172a);
        color: #f1f5f9;
    }
    .stBlock {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background: rgba(0,0,0,0.4) !important;
        color: #60a5fa !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important;
        border-radius: 12px !important;
    }
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 18px;
        font-size: 18px;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }
    h1, h2, h3 { color: #60a5fa !important; text-align: center; }
    .stProgress > div > div > div > div { background-color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك جلب البيانات السحابي (Google Sheets) ---
# رابط الجدول الخاص بك (بصيغة CSV للقراءة المباشرة)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xFLs5Qc1c1R0NIYUjuwS4K_6YcXrfIylkTDSdPYnXiE/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=15) # تحديث البيانات من جوجل كل 15 ثانية
def load_audio_library():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip().str.lower()
        if 'name' in df.columns and 'url' in df.columns:
            return dict(zip(df['name'], df['url']))
        else:
            st.error("⚠️ خطأ في أعمدة الجدول: تأكد أن العناوين هي name و url")
            return {"قائمة فارغة": ""}
    except Exception:
        return {"خطأ في الاتصال بالجدول": ""}

audio_library = load_audio_library()

# بيانات Green API (الثابتة)
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- 3. واجهة التحكم الرئيسية ---
st.markdown("<h1>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البث السحابي الذكي v16.0</p>", unsafe_allow_html=True)
st.divider()

with st.container():
    st.markdown("### 🎙️ المكتبة السحابية المباشرة")
    names = list(audio_library.keys())
    selected_audio = st.selectbox("اختر التسجيل الصوتي من جدولك:", names)
    
    current_url = audio_library.get(selected_audio, "")
    st.text_input("رابط الملف النشط:", value=current_url, disabled=True)
    
    st.markdown("### ⏲️ إعدادات الأمان (Anti-Ban)")
    # نصيحة: للباقات المجانية يفضل عدم النزول عن 10 ثواني
    delay = st.slider("الانتظار بين الرسائل (ثواني):", 2, 60, 15)

with st.expander("👥 إدارة الأهداف (Targets)", expanded=True):
    numbers_input = st.text_area("ضع الأرقام هنا (سيتم تصحيحها تلقائياً):", 
                                 height=150, 
                                 placeholder="06XXXXXXXX\n2126XXXXXXX\n+2127XXXXXXX")

# --- 4. محرك المعالجة والإرسال ---
def sanitize(phone):
    """ تنقية الرقم وتحويله للصيغة الدولية التي يطلبها واتساب (بدون +) """
    clean = re.sub(r'\D', '', str(phone))
    if clean.startswith('00212'): clean = clean[2:]
    elif clean.startswith('0'): clean = '212' + clean[1:]
    elif len(clean) == 9: clean = '212' + clean
    return clean

if st.button("تطهير وإطلاق الحملة ⚡"):
    if not current_url or not numbers_input:
        st.warning("⚠️ يرجى التأكد من اختيار تسجيل وإدخال أرقام هواتف.")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(targets)
        
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        for index, raw_num in enumerate(targets):
            final_num = sanitize(raw_num)
            
            if not final_num:
                continue
                
            endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            payload = {
                "chatId": f"{final_num}@c.us",
                "urlFile": current_url,
                "fileName": "royal_audio.ogg"
            }
            
            try:
                # محاولة الإرسال
                response = requests.post(endpoint, json=payload, timeout=30)
                
                if response.status_code == 200:
                    status_box.success(f"✅ [{index+1}/{total}] تم الإرسال بنجاح لـ: {final_num}")
                else:
                    # تحليل سبب الفشل (قيود الباقة أو الرقم)
                    res_json = response.json()
                    error_msg = res_json.get('message', 'خطأ في القيود')
                    
                    if "Constraint" in error_msg or "Developer" in error_msg:
                        status_box.error(f"❌ فشل مع {final_num}: باقة المطور تمنع الإرسال (Constraint Error)")
                    else:
                        status_box.error(f"❌ فشل مع {final_num}: {error_msg}")
            
            except Exception as e:
                status_box.error(f"❌ خطأ تقني مع الرقم {final_num}")
            
            # تحديث شريط التقدم
            progress_bar.progress((index + 1) / total)
            
            # الفاصل الزمني مع لمسة عشوائية لكسر نمط الروبوت
            if index < total - 1:
                actual_wait = delay + random.uniform(0.5, 2.0)
                time.sleep(actual_wait)

        st.balloons()
        st.success(f"✨ اكتملت المهمة! تم فحص {total} رقم.")

st.markdown("<br><hr><p style='text-align: center; color: rgba(148,163,184,0.3); font-size: 10px;'>VOX ROYAL PRO • CLOUD CONNECTED • 2026</p>", unsafe_allow_html=True)
