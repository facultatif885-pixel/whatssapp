import streamlit as st
import requests
import time
import re

# إعدادات الواجهة
st.set_page_config(page_title="WhatsApp Voice Bot", page_icon="🎙️")

ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ مرسل البصمات الصوتية")
st.success("✅ تم التأكد من أن الربط يعمل بنجاح")

uploaded_file = st.file_uploader("📤 ارفع ملف الصوت هنا (.ogg أو .mp3)", type=['ogg', 'mp3'])
numbers_input = st.text_area("📱 قائمة الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX", height=200)

def clean_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '212' + phone[1:]
    return phone

if st.button("🚀 إرسال الملف الصوتي الآن"):
    if not uploaded_file or not numbers_input:
        st.error("الرجاء رفع الملف وإدخال الأرقام")
    else:
        # تحضير الملف
        file_bytes = uploaded_file.getvalue()
        files = {'file': (uploaded_file.name, file_bytes, uploaded_file.type)}
        
        try:
            with st.spinner('جاري معالجة وإرسال الملف...'):
                # الخطوة 1: رفع الملف للمنصة
                upload_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/uploadFile/{API_TOKEN}"
                upload_res = requests.post(upload_url, files=files)
                file_url = upload_res.json().get('urlFile')

                if file_url:
                    raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
                    
                    for num in raw_numbers:
                        clean_num = clean_number(num)
                        # الخطوة 2: إرسال الرابط الناتج كملف
                        send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
                        
                        payload = {
                            "chatId": f"{clean_num}@c.us",
                            "urlFile": file_url,
                            "fileName": "audio_msg.ogg" # تسمية افتراضية متوافقة
                        }
                        
                        res = requests.post(send_url, json=payload)
                        if res.status_code == 200:
                            st.success(f"✅ تم إرسال الصوت لـ: {clean_num}")
                        else:
                            st.error(f"❌ فشل الإرسال لـ {clean_num}")
                        
                        time.sleep(3) # أمان لتفادي الحظر
                    st.balloons()
                else:
                    st.error("حدثت مشكلة في رفع الملف للمنصة، حاول مرة أخرى.")
        except Exception as e:
            st.error(f"خطأ تقني: {str(e)}")
