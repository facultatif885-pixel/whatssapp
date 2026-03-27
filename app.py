import streamlit as st
import requests
import json
import time
import re

# إعدادات الواجهة لتناسب الهاتف
st.set_page_config(page_title="WhatsApp Voice Bot", layout="centered")

# بيانات منصة Green API الخاصة بك
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ أداة إرسال الرسائل الصوتية")
st.markdown("---")

# الحقول المطلوبة
audio_url = st.text_input("🔗 رابط ملف الصوت المباشر (Direct Link)", placeholder="https://example.com/voice.ogg")
numbers_input = st.text_area("📱 أدخل الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX\n07XXXXXXXX")

def clean_number(phone):
    # تنظيف الرقم من المسافات أو الرموز
    phone = re.sub(r'\D', '', phone)
    
    # تصحيح الأرقام المغربية تلقائياً
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    elif len(phone) == 9 and (phone.startswith('6') or phone.startswith('7') or phone.startswith('5')):
        phone = '212' + phone
        
    return phone

if st.button("🚀 إطلاق الإرسال الآن"):
    if not audio_url or not numbers_input:
        st.error("الرجاء إدخال الرابط وقائمة الأرقام!")
    else:
        # تحويل النص إلى قائمة أرقام نظيفة
        raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total = len(raw_numbers)
        
        st.info(f"جاري المعالجة والإرسال إلى {total} رقم...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, raw_num in enumerate(raw_numbers):
            clean_num = clean_number(raw_num)
            url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            
            payload = {
                "chatId": f"{clean_num}@c.us",
                "urlFile": audio_url,
                "fileName": "voice_message.ogg"
            }
            
            try:
                # إرسال الطلب للمنصة
                response = requests.post(url, json=payload, timeout=20)
                if response.status_code == 200:
                    st.success(f"✅ تم الإرسال بنجاح إلى: {clean_num}")
                else:
                    st.warning(f"⚠️ فشل مع {clean_num}: تأكد من ربط الهاتف بالمنصة")
            except Exception as e:
                st.error(f"❌ خطأ فني مع الرقم {clean_num}")
            
            # تحديث شريط التقدم والانتظار قليلاً لتجنب الحظر
            progress_bar.progress((index + 1) / total)
            status_text.text(f"تم إرسال {index + 1} من أصل {total}")
            time.sleep(3) 

        st.balloons()
        st.success("✅ انتهت العملية بنجاح!")
