import streamlit as st
import requests
import time
import re
import random

# --- 1. إعدادات النظام المظهر الملكي ---
st.set_page_config(
    page_title="VOX ROYAL PRO - v13",
    page_icon="👑",
    layout="centered"
)

# تصميم SANDIZ المطور (CSS)
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
        color: white; border: none; border-radius: 12px; padding: 18px;
        font-size: 20px; font-weight: bold; text-transform: uppercase;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3); transition: 0.3s;
    }
    div.stButton > button:first-child:hover { transform: scale(1.01); background: #3b82f6; }
    h1, h2, h3 { color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# بيانات الاعتماد
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- 2. إدارة مخزن الروابط (Session State) ---
if 'audio_library' not in st.session_state:
    st.session_state.audio_library = {"رابط افتراضي": ""}

# --- 3. واجهة التحكم (Command Center) ---
st.markdown("<h1 style='text-align: center;'>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>نظام البث الذكي مع مخزن الروابط v13</p>", unsafe_allow_html=True)
st.divider()

# --- قسم حفظ الروابط ---
with st.expander("💾 إدارة مخزن الروابط (Audio Library)", expanded=False):
    col1, col2 = st.columns([2, 1])
    with col1:
        new_url = st.text_input("ضع الرابط الجديد هنا")
    with col2:
        new_name = st.text_input("اسم الرابط (مثلا: عرض 1)")
    
    if st.button("حفظ في المخزن ✨"):
        if new_url and new_name:
            st.session_state.audio_library[new_name] = new_url
            st.success(f"تم حفظ '{new_name}' بنجاح!")
        else:
            st.warning("عمر الخانات بجوج باش تحفظ.")

# --- قسم إعدادات الإرسال ---
with st.container():
    st.markdown("### 🎙️ إعدادات الحملة")
    
    # اختيار من المخزن
    saved_options = list(st.session_state.audio_library.keys())
    selected_name = st.selectbox("اختر رابطاً محفظاً أو ادخل يدوياً:", saved_options)
    
    final_audio_link = st.text_input("الرابط المعتمد حالياً:", 
                                     value=st.session_state.audio_library[selected_name],
                                     placeholder="https://raw.githubusercontent.com/...")

    # نظام الانتظار المطور
    st.markdown("### ⏲️ نظام الحماية (Anti-Ban)")
    delay_seconds = st.slider("مدة الانتظار بين كل رسالة (ثانية):", 
                               min_value=2, max_value=60, value=5,
                               help="كلما زاد الوقت، قل خطر الحظر.")

# --- قاعدة الأهداف ---
with st.expander("👥 قاعدة بيانات الأهداف (Targets)", expanded=True):
    numbers_input = st.text_area("سجل الأرقام (أدخل الأرقام بأي صيغة)", height=150)

st.divider()

# --- محرك التطهير والإرسال ---
def sanitize_phone(phone):
    clean = re.sub(r'\D', '', phone)
    if clean.startswith('00212'): clean = clean[2:]
    elif clean.startswith('0'): clean = '212' + clean[1:]
    elif len(clean) == 9: clean = '212' + clean
    return clean

if st.button("تطهير، مطابقة وإطلاق ⚡"):
    if not final_audio_link or not numbers_input:
        st.error("⚠️ ناقصك الرابط ولا الأرقام!")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(targets)
        
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        for index, raw_num in enumerate(targets):
            final_num = sanitize_phone(raw_num)
            endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            
            payload = {
                "chatId": f"{final_num}@c.us",
                "urlFile": final_audio_link,
                "fileName": "royal_audio.ogg"
            }
            
            try:
                res = requests.post(endpoint, json=payload, timeout=25)
                if res.status_code == 200:
                    status_box.success(f"✅ [{index+1}/{total}] تم الإرسال لـ: {final_num}")
                else:
                    status_box.error(f"❌ فشل مع: {final_num}")
            except:
                status_box.error(f"❌ خطأ اتصال مع: {final_num}")
            
            # تحديث التقدم
            progress_bar.progress((index + 1) / total)
            
            # نظام الانتظار الذكي (إضافة عشوائية بسيطة لتبدو كبشر)
            if index < total - 1:
                actual_delay = delay_seconds + random.uniform(0.5, 1.5)
                time.sleep(actual_delay)

        st.balloons()
        st.success("✨ المهمة انتهت بنجاح!")

st.markdown("<p style='text-align: center; color: rgba(148,163,184,0.3); font-size: 10px;'>VOX ROYAL PRO • ANTI-BAN SYSTEM • 2026</p>", unsafe_allow_html=True)
