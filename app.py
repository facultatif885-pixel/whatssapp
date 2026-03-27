import streamlit as st
import requests
import time
import re

# إعدادات الواجهة
st.set_page_config(page_title="WhatsApp Link Sender", page_icon="🎙️")

ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ مرسل الصوت عبر الروابط المباشرة")
st.markdown("---")

# خانة وضع الرابط المباشر
audio_link = st.text_input("🔗 ضع رابط الملف الصوتي المباشر هنا", placeholder="https://example.com/voice.ogg")
st.caption("يجب أن ينتهي الرابط بـ .mp3 أو .ogg")

# خانة وضع الأرقام
numbers_input = st.text_area("📱 قائمة الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX", height=200)

def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    return phone

if st.button("🚀 إرسال الآن"):
    if not audio_link or not numbers_input:
        st.error("الرجاء إدخال الرابط وقائمة الأرقام!")
    else:
        raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        st.info(f"جاري الإرسال إلى {len(raw_numbers)} رقم...")
        
        for num in raw_numbers:
            clean_num = clean_number(num)
            send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            
            payload = {
                "chatId": f"{clean_num}@c.us",
                "urlFile": audio_link, # الرابط الخارجي الذي وضعته
                "fileName": "audio_message.ogg"
            }
            
            try:
                res = requests.post(send_url, json=payload)
                if res.status_code == 200:
                    st.success(f"✅ تم الطلب لـ: {clean_num}")
                else:
                    st.error(f"❌ فشل مع {clean_num}: {res.text}")
            except Exception as e:
                st.error(f"خطأ: {str(e)}")
            
            time.sleep(3)
        st.balloons()
