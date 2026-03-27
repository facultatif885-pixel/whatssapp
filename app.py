import streamlit as st
import requests

# بياناتك
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

st.title("اختبار ربط الواتساب")
number = st.text_input("أدخل رقمك للتجربة (مثلاً 212600000000)")

if st.button("إرسال رسالة تجريبية"):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": f"{number}@c.us",
        "message": "أهلاً، إذا وصلت هذه الرسالة فإن الربط سليم 100%"
    }
    res = requests.post(url, json=payload)
    st.write(res.json())
