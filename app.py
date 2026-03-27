import streamlit as st
import requests
import time
import re

# إعدادات الواجهة
st.set_page_config(page_title="WhatsApp Voice Bot", page_icon="🎙️")

# بيانات Green API الخاصة بك
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ مرسل الملفات الصوتية")
st.markdown("---")

# رفع الملف والأرقام
uploaded_file = st.file_uploader("📤 اختر ملف الصوت (.ogg أو .mp3)", type=['ogg', 'mp3'])
numbers_input = st.text_area("📱 أدخل الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX", height=200)

def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    return phone

if st.button("🚀 بدء الإرسال الآن"):
    if not uploaded_file or not numbers_input:
        st.error("الرجاء إدخال البيانات المطلوبة!")
    else:
        # 1. رفع الملف للحصول على رابط
        upload_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/uploadFile/{API_TOKEN}"
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        try:
            with st.spinner('جاري الرفع...'):
                upload_res = requests.post(upload_url, files=files)
                file_url = upload_res.json().get('urlFile')

            if file_url:
                raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
                st.info(f"جاري الإرسال إلى {len(raw_numbers)} رقم...")
                
                for num in raw_numbers:
                    clean_num = clean_number(num)
                    send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
                    
                    # تم حذف isPtt لتجنب خطأ الـ Validation
                    payload = {
                        "chatId": f"{clean_num}@c.us",
                        "urlFile": file_url,
                        "fileName": "audio_message.mp3" 
                    }
                    
                    res = requests.post(send_url, json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ تم الإرسال لـ: {clean_num}")
                    else:
                        st.error(f"❌ فشل مع {clean_num}: {res.json().get('message')}")
                    
                    time.sleep(3) # فتره زمنية لتجنب الحظر
                st.balloons()
            else:
                st.error("فشل في الحصول على رابط للملف من المنصة.")
        except Exception as e:
            st.error(f"حدث خطأ فني: {str(e)}")
