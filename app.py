import streamlit as st
import requests
import time
import re

# إعدادات واجهة المستخدم للهاتف
st.set_page_config(page_title="WhatsApp Voice Sender", page_icon="🎙️", layout="centered")

# بيانات Green API الخاصة بك
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("🎙️ مرسل البصمات الصوتية الآلي")
st.info("تأكد أن الـ Instance في منصة Green API حالتها Authorized قبل البدء.")

# --- الواجهة ---
uploaded_file = st.file_uploader("📤 اختر ملف الصوت (.ogg أو .mp3)", type=['ogg', 'mp3'])
numbers_input = st.text_area("📱 أدخل الأرقام (رقم في كل سطر)", placeholder="06XXXXXXXX\n07XXXXXXXX", height=200)

def clean_number(phone):
    """تنظيف وتصحيح الرقم للصيغة الدولية"""
    phone = re.sub(r'\D', '', phone) # حذف أي رموز غير رقمية
    if phone.startswith('0'):
        phone = '212' + phone[1:] # تحويل من 06 إلى 2126
    elif len(phone) == 9 and (phone.startswith('6') or phone.startswith('7')):
        phone = '212' + phone
    return phone

# --- زر التشغيل ---
if st.button("🚀 إطلاق الإرسال الآن"):
    if not uploaded_file or not numbers_input:
        st.error("الرجاء رفع ملف صوتي وكتابة الأرقام!")
    else:
        # 1. رفع الملف للمنصة للحصول على رابط مؤقت (Upload)
        upload_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/uploadFile/{API_TOKEN}"
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        try:
            with st.spinner('جاري معالجة ورفع الملف...'):
                upload_res = requests.post(upload_url, files=files)
                
            if upload_res.status_code == 200:
                file_url = upload_res.json().get('urlFile')
                
                # 2. البدء في الإرسال لكل رقم
                raw_numbers = [n.strip() for n in numbers_input.split('\n') if n.strip()]
                total = len(raw_numbers)
                st.write(f"⏳ جاري الإرسال إلى {total} رقم...")
                
                progress_bar = st.progress(0)
                
                for index, num in enumerate(raw_numbers):
                    target_num = clean_number(num)
                    send_url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
                    
                    payload = {
                        "chatId": f"{target_num}@c.us",
                        "urlFile": file_url,
                        "fileName": "voice_message.ogg",
                        "isPtt": True # تحويل الملف إلى "رسالة صوتية" حقيقية
                    }
                    
                    # طلب الإرسال
                    response = requests.post(send_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success(f"✅ تم الإرسال لـ: {target_num}")
                    else:
                        st.error(f"❌ فشل مع {target_num}: {response.text}")
                    
                    # تحديث شريط التقدم وانتظار بسيط لتفادي الحظر
                    progress_bar.progress((index + 1) / total)
                    time.sleep(2) 
                
                st.balloons()
                st.success("✨ انتهت المهمة بنجاح!")
            else:
                st.error(f"فشل رفع الملف للمنصة: {upload_res.text}")
                
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {str(e)}")

# تذييل الصفحة
st.markdown("---")
st.caption("برمجة مخصصة لمنصة Green API و WhatsApp")
