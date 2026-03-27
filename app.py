import streamlit as st
import requests
import time
import re

# إعدادات الواجهة
st.set_page_config(page_title="WhatsApp Voice Bot", layout="centered")

# بيانات Green API الخاصة بك (ثابتة وجاهزة)
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ مرسل الرسائل الصوتية الذكي")
st.markdown("---")

# 1. خيار رفع الملف الصوتي مباشرة
uploaded_file = st.file_uploader("📤 اختر ملف الصوت من هاتفك (.ogg أو .mp3)", type=['ogg', 'mp3'])

# 2. مكان إدخال الأرقام
numbers_input = st.text_area("📱 أدخل الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX\n07XXXXXXXX", height=200)

def clean_number(phone):
    phone = re.sub(r'\D', '', phone) # حذف الرموز
    if phone.startswith('0'): # تحويل أرقام المغرب للصيغة الدولية
        phone = '212' + phone[1:]
    elif len(phone) == 9:
        phone = '212' + phone
    return phone

if st.button("🚀 إطلاق الإرسال الآن"):
    if not uploaded_file or not numbers_input:
        st.error("الرجاء رفع ملف صوتي وإدخال الأرقام أولاً!")
    else:
        # تجهيز الملف للإرسال (رفع مؤقت لـ Green API)
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        # أولاً: رفع الملف للمنصة لجلب رابط مؤقت
        upload_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/uploadFile/{API_TOKEN}"
        
        try:
            with st.spinner('جاري تجهيز الملف...'):
                upload_res = requests.post(upload_url, files=files)
                file_url = upload_res.json().get('urlFile')

            if file_url:
                raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
                st.info(f"جاري الإرسال إلى {len(raw_numbers)} رقم...")
                
                for num in raw_numbers:
                    clean_num = clean_number(num)
                    send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
                    payload = {
                        "chatId": f"{clean_num}@c.us",
                        "urlFile": file_url,
                        "fileName": "voice.ogg"
                    }
                    
                    res = requests.post(send_url, json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ تم الإرسال لـ: {clean_num}")
                    else:
                        st.warning(f"⚠️ فشل مع: {clean_num}")
                    
                    time.sleep(2) # تأخير لتجنب الحظر
                st.balloons()
            else:
                st.error("فشل رفع الملف للمنصة، تأكد من إعدادات Green API.")
        except Exception as e:
            st.error(f"حدث خطأ فني: {str(e)}")
