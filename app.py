import streamlit as st
import requests
import time
import re

# --- 1. إعدادات الصفحة والمظهر الملكي ---
st.set_page_config(
    page_title="send message pro",
    page_icon="🚀",
    layout="centered"
)

# تطبيق الديزاين الأزرق الملكي باستخدام CSS
st.markdown("""
    <style>
    /* خلفية التطبيق المتدرجة */
    .stApp {
        background: radial-gradient(circle, #1e3a8a, #0f172a);
        color: #f1f5f9;
    }
    
    /* الحاوية الرئيسية (Glassmorphism) */
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    /* تحسين شكل الحقول */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(0,0,0,0.3) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }

    /* زر الإرسال الأزرق */
    div.stButton > button:first-child {
        width: 100%;
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }
    
    div.stButton > button:first-child:hover {
        background: #1d4ed8;
        transform: translateY(-2px);
    }

    h1, h2, h3 {
        color: #60a5fa !important;
    }
    
    .stMarkdown p {
        color: #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

# بيانات Green API (الثابتة)
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- 2. واجهة المستخدم (UI) ---
st.markdown("<h1 style='text-align: center;'>🚀 SANDIZ VOICE v12</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظام الإرسال الذكي للبصمات الصوتية</p>", unsafe_allow_html=True)

with st.container():
    st.markdown("### 📥 الإعدادات والمدخلات")
    
    # حقل الرابط المباشر
    audio_link = st.text_input("🔗 رابط الملف الصوتي (Direct Raw Link)", 
                               placeholder="https://raw.githubusercontent.com/...")

    # حقل الأرقام
    numbers_input = st.text_area("📱 قائمة الأرقام المستهدفة", 
                                 placeholder="أدخل الأرقام هنا، رقم في كل سطر...", 
                                 height=250)
    
    st.caption("سيتم معالجة الأرقام ومطابقتها دولياً تلقائياً.")

st.markdown("---")

# --- 3. منطق الإرسال ---
def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    elif len(phone) == 9:
        phone = '212' + phone
    return phone

if st.button("تصحيح وإطلاق ⚡"):
    if not audio_link or not numbers_input:
        st.error("❌ يرجى إدخال الرابط وقائمة الأرقام.")
    else:
        raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(raw_numbers)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        st.toast("🧠 جاري التحليل والربط...")
        
        for index, num in enumerate(raw_numbers):
            clean_num = clean_number(num)
            send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            
            payload = {
                "chatId": f"{clean_num}@c.us",
                "urlFile": audio_link,
                "fileName": "audio_message.ogg"
            }
            
            try:
                res = requests.post(send_url, json=payload, timeout=20)
                if res.status_code == 200:
                    status_text.success(f"✅ تم الإرسال بنجاح إلى: {clean_num}")
                else:
                    status_text.error(f"❌ فشل مع: {clean_num}")
            except:
                status_text.error(f"❌ خطأ في الاتصال بالرقم {clean_num}")
            
            # تحديث التقدم
            progress_bar.progress((index + 1) / total)
            time.sleep(2) # تأخير بسيط للحماية

        st.balloons()
        st.success("✨ تمت المهمة بنجاح!")

# التذييل
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.3); font-size: 12px; margin-top: 50px;'>SANDIZ AI SYSTEM • 2026</p>", unsafe_allow_html=True)
