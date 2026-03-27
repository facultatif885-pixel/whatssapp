
import streamlit as st
import requests
import time
import re

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="WhatsApp Pro Sender",
    page_icon="📲",
    layout="centered"
)

# 2. تصميم CSS المطور (تم تصحيح الخطأ هنا)
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #25D366;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 18px;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #128C7E;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# بيانات Green API الثابتة
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- الواجهة (UI) ---
st.markdown("<h1 style='text-align: center; color: #075E54;'>🚀 WhatsApp Pro Sender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>أداة إرسال البصمات الصوتية الاحترافية</p>", unsafe_allow_html=True)
st.divider()

# مدخلات المستخدم
audio_link = st.text_input("🔗 رابط الملف الصوتي المباشر (Raw)", 
                           placeholder="https://raw.githubusercontent.com/...")

numbers_input = st.text_area("📱 قائمة الأرقام (رقم في كل سطر)", 
                             placeholder="06XXXXXXXX\n07XXXXXXXX", 
                             height=200)

def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    elif len(phone) == 9:
        phone = '212' + phone
    return phone

st.divider()

# زر الإرسال
if st.button("إرسال الآن 🎙️"):
    if not audio_link or not numbers_input:
        st.warning("⚠️ يرجى إدخال الرابط والأرقام أولاً.")
    else:
        raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(raw_numbers)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, num in enumerate(raw_numbers):
            clean_num = clean_number(num)
            send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            
            payload = {
                "chatId": f"{clean_num}@c.us",
                "urlFile": audio_link,
                "fileName": "voice_message.ogg"
            }
            
            try:
                res = requests.post(send_url, json=payload, timeout=20)
                if res.status_code == 200:
                    status_text.success(f"✅ تم الإرسال لـ: {clean_num}")
                else:
                    status_text.error(f"❌ فشل مع {clean_num}")
            except:
                status_text.error(f"❌ خطأ اتصال مع {clean_num}")
            
            # تحديث التقدم
            progress_bar.progress((index + 1) / total)
            time.sleep(3) # أمان

        st.balloons()
        st.success("✨ اكتملت العملية!")

# التذييل
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999; font-size: 12px;'>Powered by Gemini & Green API</p>", unsafe_allow_html=True)
