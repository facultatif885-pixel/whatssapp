import streamlit as st
import requests
import time
import re

# 1. إعدادات الصفحة الأساسية وتحسين المظهر للهاتف
st.set_page_config(
    page_title="WhatsApp Voice Sender",
    page_icon="📲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تصميم مخصص باستخدام CSS لجعل الأزرار والحقول تبدو كالتطبيقات
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #25D366;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 18px;
    }
    .stTextInput>div>div>input {
        border-radius: 15px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 15px;
    }
    .stAlert {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_name=True)

# بيانات Green API (ثابتة)
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- الهيدر (Header) ---
st.markdown("<h1 style='text-align: center; color: #075E54;'>🚀 WhatsApp Pro Sender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>أرسل بصماتك الصوتية بلمسة واحدة</p>", unsafe_allow_html=True)
st.divider()

# --- قسم الإدخال (Input Section) ---
with st.container():
    st.subheader("🔗 إعدادات الوسائط")
    audio_link = st.text_input("رابط الملف الصوتي المباشر (Raw Link)", 
                               placeholder="https://raw.githubusercontent.com/...",
                               help="انسخ رابط Raw من GitHub")
    
    st.subheader("📱 قائمة الأرقام")
    numbers_input = st.text_area("أدخل الأرقام هنا (رقم في كل سطر)", 
                                 placeholder="06XXXXXXXX\n07XXXXXXXX", 
                                 height=200)
    
    st.caption("سيتم إضافة كود الدولة (212) تلقائياً للأرقام المغربية.")

st.divider()

# --- منطق الإرسال (Logic) ---
def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    elif len(phone) == 9:
        phone = '212' + phone
    return phone

# زر الإرسال بتصميم عريض
if st.button("إرسال الآن 🎙️"):
    if not audio_link or not numbers_input:
        st.warning("⚠️ يرجى تعبئة جميع الحقول قبل البدء.")
    else:
        raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(raw_numbers)
        
        # عرض التقدم بشكل جميل
        progress_text = "جاري الإرسال.. يرجى الانتظار"
        my_bar = st.progress(0, text=progress_text)
        
        status_area = st.empty() # مكان لتحديث الحالة لكل رقم
        
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
                    status_area.success(f"✅ تم الإرسال بنجاح إلى: {clean_num}")
                else:
                    status_area.error(f"❌ فشل الإرسال لـ: {clean_num}")
            except:
                status_area.error(f"❌ خطأ في الاتصال مع الرقم: {clean_num}")
            
            # تحديث شريط التقدم
            percent_complete = (index + 1) / total
            my_bar.progress(percent_complete, text=f"تم إرسال {index + 1} من أصل {total}")
            time.sleep(3) # تأخير للحماية من الحظر

        st.balloons()
        st.success("✨ اكتملت جميع المهام بنجاح!")

# --- التذييل (Footer) ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 12px; color: #999;'>بواسطة Gemini AI • متوافق مع Green API</p>", unsafe_allow_html=True)
