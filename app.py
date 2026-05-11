import streamlit as st
import google.generativeai as genai
import PIL.Image
import os
from dotenv import load_dotenv
from datetime import datetime

# --- 1. การตั้งค่าพื้นฐาน ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ไม่พบ API Key ในไฟล์ .env")
    st.stop()

genai.configure(api_key=api_key)

# ระบบจัดการภาษา UI
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "ไทย"

# รายชื่อภาษาที่รองรับ (ใช้ร่วมกันทั้งต้นทางและปลายทาง)
LANG_OPTIONS = ["English", "Japanese", "Korean", "Chinese", "French", "German", "Thai", "Spanish"]

texts = {
    "ไทย": {
        "title": "AI แปลภาษาเพื่อการเรียนรู้", "settings": "⚙️ ตั้งค่า", "ui_lang_label": "ภาษาแอป:",
        "source": "จากภาษา:", "target": "แปลเป็น:", "history": "📜 ประวัติ",
        "clear_btn": "🗑️ ล้างประวัติ", "input_header": "📝 AI Explainable Translation",
        "placeholder": "พิมพ์ประโยคที่นี่...", "expander": "📷 หรือแปลจากรูปภาพ",
        "main_btn": "เริ่มวิเคราะห์", "result_header": "📖 ผลการวิเคราะห์",
        "tabs": ["🎯 คำแปล", "🔍 ไวยากรณ์", "💡 คำศัพท์", "🎭 บริบท"],
        "info": "กรุณาใส่ข้อมูลทางฝั่งซ้ายเพื่อเริ่มวิเคราะห์"
    },
    "English": {
        "title": "AI Explainable Translation", "settings": "⚙️ Settings", "ui_lang_label": "App Language:",
        "source": "From:", "target": "To:", "history": "📜 History",
        "clear_btn": "🗑️ Clear History", "input_header": "📝 AI Explainable Translation",
        "placeholder": "Type here...", "expander": "📷 Or from Image",
        "main_btn": "Start Analysis 🚀", "result_header": "📖 Result",
        "tabs": ["🎯 Translation", "🔍 Grammar", "💡 Vocab", "🎭 Context"],
        "info": "Please input data on the left" 
    },
    "Chinese": {
        "title": "AI Explainable Translation", "settings": "⚙️ 设置", "ui_lang_label": "软件语言:",
        "source": "原文:", "target": "目标语:", "history": "📜 历史",
        "clear_btn": "🗑️ 清除历史", "input_header": "📝 开始学习",
        "placeholder": "在此输入...", "expander": "📷 หรือจากรูปภาพแปล",
        "main_btn": "开始分析 🚀", "result_header": "📖 分析结果",
        "tabs": ["🎯 翻译", "🔍 语法", "💡 词语", "🎭 背景"],
        "info": "请在左侧输入内容"
    }
}

t = texts[st.session_state.ui_lang]

st.set_page_config(page_title=t["title"], page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

# --- 2. สมองกล AI ---
def analyze_language_content(input_data, source_lang, target_lang, is_image=False):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') 
        # ปรับ Prompt เล็กน้อยเพื่อเลี่ยงการคัดลอกเนื้อหาลิขสิทธิ์ (Recitation)
        prompt = f"""
        คุณคือครูสอนภาษาผู้เชี่ยวชาญ จงวิเคราะห์และสรุปเนื้อหาภาษา {source_lang} 
        โดยใช้คำพูดของคุณเอง (ห้ามคัดลอกข้อความจากแหล่งที่มาโดยตรง) 
        และสรุปผลตามโครงสร้างด้านล่างนี้ (ใช้ Markdown หัวข้อใหญ่):
        ### [TRANS]
        (แปลเป็นภาษา {target_lang} ด้วยสำนวนที่เหมาะสม)
        ### [GRAMMAR]
        (สรุปหลักไวยากรณ์ที่น่าสนใจจากเนื้อหานี้)
        ### [VOCAB]
        (ตารางคำศัพท์: คำศัพท์ | คำอ่าน | ความหมาย)
        ### [CULTURE]
        (เกร็ดความรู้ทางภาษาหรือวัฒนธรรม)
        """
        if is_image:
            img = PIL.Image.open(input_data)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(f"{prompt}\n\nเนื้อหาที่ต้องวิเคราะห์: {input_data}")
        
        # ตรวจสอบว่ามีข้อมูลส่งกลับมาไหมก่อนเรียก .text
        if response.candidates[0].finish_reason == 4:
            return "⚠️ ไม่สามารถแสดงผลได้เนื่องจากเนื้อหาใกล้เคียงกับแหล่งข้อมูลที่มีลิขสิทธิ์มากเกินไป กรุณาลองเปลี่ยนประโยคใหม่"
            
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') 
        prompt = f"""
        คุณคือครูสอนภาษาผู้เชี่ยวชาญ วิเคราะห์เนื้อหาภาษา {source_lang} 
        และสรุปผลตามโครงสร้างด้านล่างนี้ (ใช้ Markdown หัวข้อใหญ่):
        ### [TRANS]
        (เขียนคำแปลเป็น {target_lang} ที่นี่)
        ### [GRAMMAR]
        (เขียนอธิบายไวยากรณ์และโครงสร้างประโยคที่นี่)
        ### [VOCAB]
        (สร้างตารางคำศัพท์: คำศัพท์ | คำอ่าน | ความหมาย)
        ### [CULTURE]
        (เขียนเกร็ดความรู้ทางภาษาหรือวัฒนธรรมที่นี่)
        """
        if is_image:
            img = PIL.Image.open(input_data)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(f"{prompt}\n\nเนื้อหา: {input_data}")
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- 3. แถบข้าง (Sidebar) ---
with st.sidebar:
    st.title(t["title"])
    ui_choice = st.selectbox(t["ui_lang_label"], ["ไทย", "English", "Chinese"], 
                               index=["ไทย", "English", "Chinese"].index(st.session_state.ui_lang))
    if ui_choice != st.session_state.ui_lang:
        st.session_state.ui_lang = ui_choice
        st.rerun()

    st.divider()
    if st.button(t["clear_btn"]):
        st.session_state.history = []
        if "current_view" in st.session_state: del st.session_state.current_view
        st.rerun()

    for i, item in enumerate(reversed(st.session_state.history)):
        if st.button(f"🕒 {item['time']} | {item['label']}", key=f"h_{i}"):
            st.session_state.current_view = item['result']

# --- 4. หน้าจอหลัก ---
col_input, col_result = st.columns([1, 1.5], gap="large")

with col_input:
    st.markdown(f"### {t['input_header']}")
    l1, l2 = st.columns(2)
    with l1:
        source_lang = st.selectbox(t["source"], ["Auto-detect"] + LANG_OPTIONS)
    with l2:
        target_lang = st.selectbox(t["target"], LANG_OPTIONS)

    user_text = st.text_area("Input", label_visibility="collapsed", placeholder=t["placeholder"], height=150)
    with st.expander(t["expander"]):
        uploaded_file = st.file_uploader("Upload", label_visibility="collapsed", type=['jpg', 'jpeg', 'png'])
        # ส่วนที่เพิ่มเพื่อให้เห็นภาพเต็มๆ
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
    
    if st.button(t["main_btn"]):
        with st.spinner('Analysing...'):
            res = None
            if uploaded_file:
                res = analyze_language_content(uploaded_file, source_lang, target_lang, is_image=True)
                lbl = "🖼️ Image"
            elif user_text.strip():
                res = analyze_language_content(user_text, source_lang, target_lang, is_image=False)
                lbl = user_text[:12] + "..."
            
            if res:
                now = datetime.now().strftime("%H:%M")
                st.session_state.history.append({"time": now, "label": lbl, "result": res})
                st.session_state.current_view = res
                st.rerun()

with col_result:
    st.markdown(f"### {t['result_header']}")
    if "current_view" in st.session_state:
        raw = st.session_state.current_view
        tab1, tab2, tab3, tab4 = st.tabs(t["tabs"])
        try:
            with tab1: st.info(raw.split("### [TRANS]")[-1].split("### [GRAMMAR]")[0].strip())
            with tab2: st.markdown(raw.split("### [GRAMMAR]")[-1].split("### [VOCAB]")[0].strip())
            with tab3: st.markdown(raw.split("### [VOCAB]")[-1].split("### [CULTURE]")[0].strip())
            with tab4: st.warning(raw.split("### [CULTURE]")[-1].strip())
        except: st.markdown(raw)
    else:
        st.info(t["info"])

st.divider()
st.caption("LearnLingua AI | Multi-language Support | Powered by Gemini 2.5 Flash")