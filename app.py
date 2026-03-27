import streamlit as st
import requests
import time
import re

# --- 1. إعدادات النظام المظهر الملكي ---
st.set_page_config(
    page_title="VOX ROYAL PRO",
    page_icon="👑",
    layout="centered"
)

# تطبيق ديزاين SANDIZ المطور بألوان ملكية
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1e3a8a, #0f172a);
        color: #f1f5f9;
    }
    .stBlock {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(0,0,0,0.4) !important;
        color: #60a5fa !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important;
        border-radius: 12px !important;
    }
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 18px;
        font-size: 20px;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        transform: scale(1.01);
    }
    h1, h2, h3 { color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# بيانات الاعتماد المشفرة
ID_INSTANCE = "7107566642"
API_TOKEN = "257db6c4dc0d4ed6a1471041b2964da6579c2986afca4a2cbc"

# --- 2. واجهة التحكم (Command Center) ---
st.markdown("<h1 style='text-align: center;'>👑 VOX ROYAL PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>منصة البث الصوتي الآلي • ذكاء المطابقة v12.5</p>", unsafe_allow_html=True)
st.divider()

with st.expander("📦 مخزن الوسائط (Media Vault)", expanded=True):
    audio_link = st.text_input("🔗 رابط البصمة الصوتية المباشر", placeholder="https://raw.githubusercontent.com/...")

with st.expander("👥 قاعدة بيانات الأهداف (Targets)", expanded=True):
    numbers_input = st.text_area("📱 سجل الأرقام المستهدفة", 
                                 placeholder="أدخل الأرقام بأي صيغة (+212... أو 06... أو 00212...)", 
                                 height=200)
    st.caption("💡 سيقوم المحرك بتنظيف الأرقام تلقائياً وحذف الرموز والمسافات.")

st.divider()

# --- 3. محرك التطهير والمطابقة الذكي (Smart Sanitizer) ---
def sanitize_phone(phone):
    # 1. إزالة كافة الرموز غير الرقمية (المسافات، +, -, الأقواس)
    clean_phone = re.sub(r'\D', '', phone)
    
    # 2. إذا بدأ بـ 00212، نحذف الـ 00 لتصبح 212
    if clean_phone.startswith('00212'):
        clean_phone = clean_phone[2:]
    
    # 3. إذا بدأ بـ 06 أو 07 أو 05 (رقم مغربي محلي)
    elif clean_phone.startswith('0'):
        clean_phone = '212' + clean_phone[1:]
    
    # 4. إذا كان الرقم يتكون من 9 أرقام فقط (بدون الصفر وبدون الكود الدولي)
    elif len(clean_phone) == 9:
        clean_phone = '212' + clean_phone
        
    return clean_phone

# زر التشغيل النهائي
if st.button("تطهير، مطابقة وإطلاق ⚡"):
    if not audio_link or not numbers_input:
        st.error("⚠️ يرجى تزويد النظام بالبيانات المطلوبة.")
    else:
        targets = [n.strip() for n in numbers_input.split('\n') if n.strip()]
        total_targets = len(targets)
        
        progress_bar = st.progress(0)
        status_update = st.empty()
        
        for index, raw_num in enumerate(targets):
            # تفعيل محرك التطهير
            final_num = sanitize_phone(raw_num)
            
            endpoint = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUrl/{API_TOKEN}"
            payload = {
                "chatId": f"{final_num}@c.us",
                "urlFile": audio_link,
                "fileName": "royal_voice.ogg"
            }
            
            try:
                response = requests.post(endpoint, json=payload, timeout=25)
                if response.status_code == 200:
                    status_update.success(f"✅ تم التطهير والإرسال للهدف: {final_num}")
                else:
                    status_update.error(f"❌ فشل الإرسال للرقم: {final_num}")
            except:
                status_update.error(f"❌ خطأ تقني مع الرقم: {final_num}")
            
            progress_bar.progress((index + 1) / total_targets)
            time.sleep(2.5) 

        st.balloons()
        st.success(f"✨ اكتملت العملية لـ {total_targets} هدف!")

st.markdown("<br><hr><p style='text-align: center; color: rgba(148, 163, 184, 0.4); font-size: 11px;'>VOX ROYAL PRO • SMART MATCHING ENGINE • 2026</p>", unsafe_allow_html=True)
