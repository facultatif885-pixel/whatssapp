import streamlit as st
import requests
import json
import time
import re

# إعدادات الصفحة للهاتف
st.set_page_config(page_title="WhatsApp Voice Sender", layout="centered")

st.title("🎙️ مرسل الرسائل الصوتية - Green API")
st.markdown("---")

# مدخلات الإعدادات (يمكن إخفاؤها في ملف .env لاحقاً)
with st.expander("⚙️ إعدادات الربط (Green API)"):
    id_instance = st.text_input("ID Instance", type="password")
    api_token = st.text_input("API Token", type="password")

# واجهة إدخال البيانات
audio_url = st.text_input("🔗 رابط ملف الصوت (Direct Link)", placeholder="https://example.com/audio.ogg")
numbers_input = st.text_area("📱 أدخل الأرقام (رقم في كل سطر)", placeholder="0600000000\n212700000000")

def clean_number(phone):
    # إزالة أي رموز غير رقمية
    phone = re.sub(r'\D', '', phone)
    # إذا بدأ بـ 06 أو 07 (أرقام المغرب) نضيف 212
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    # إذا كان الرقم دولياً ولا يبدأ بـ 212 (تعديل حسب الحاجة)
    elif len(phone) == 9 and not phone.startswith('212'):
        phone = '212' + phone
    return phone

if st.button("🚀 إطلاق الإرسال"):
    if not id_instance or not api_token or not audio_url or not numbers_input:
        st.error("الرجاء ملء جميع الحقول!")
    else:
        numbers_list = [clean_number(n.strip()) for n in numbers_input.split('\n') if n.strip()]
        
        st.info(f"جاري الإرسال إلى {len(numbers_list)} رقم...")
        progress_bar = st.progress(0)
        
        for index, num in enumerate(numbers_list):
            url = f"https://api.green-api.com/waInstance{id_instance}/sendFileByUrl/{api_token}"
            payload = {
                "chatId": f"{num}@c.us",
                "urlFile": audio_url,
                "fileName": "voice.ogg"
            }
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    st.success(f"✅ تم الإرسال إلى: {num}")
                else:
                    st.warning(f"⚠️ فشل مع {num}: {response.text}")
            except Exception as e:
                st.error(f"❌ خطأ في الرقم {num}: {str(e)}")
            
            # تحديث شريط التقدم
            progress_bar.progress((index + 1) / len(numbers_list))
            time.sleep(2) # تأخير لتجنب الحظر

        st.balloons()
        st.success("كتملت العملية!")
