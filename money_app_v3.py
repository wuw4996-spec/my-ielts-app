import streamlit as st
from openai import OpenAI
import os
import google.generativeai as genai
from PIL import Image

# --- 1. 页面配置 (必须放在最前面) ---
st.set_page_config(page_title="雅思作文改分王", page_icon="💰")


# --- 2. 核心功能函数定义 (修复缺失定义的问题) ---

def upload_to_gemini(img_file):
    # ... (之前的代码)
    # 尝试使用 models/ 前缀，这是目前最标准的写法
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        img = Image.open(img_file)
        response = model.generate_content(["请提取图中英文", img])
        return response.text
    except Exception as e:
        # 如果 flash 找不到，回退到 pro 版本
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        img = Image.open(img_file)
        response = model.generate_content(["请提取图中英文", img])
        return response.text


def get_ielts_feedback(essay_content, api_key):
    """批改函数：调用 DeepSeek 进行评分"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    prompt = f"""你是一位严格的雅思写作前考官。请对以下作文进行专业测评：
    {essay_content}
    请按格式输出：## 📊 测评成绩单、## 📝 详细批改、## 💡 词汇升级、## 🏆 满分范文。"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个专业的雅思作文批改专家。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def load_valid_keys():
    """读取本地激活码文件"""
    file_path = "keys.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("ADMIN123\n")
        return ["ADMIN123"]
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


# --- 3. 样式注入 ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stTextArea textarea { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API Key 配置 ---
admin_api_key = st.secrets.get("DEEPSEEK_API_KEY") or st.sidebar.text_input("管理员 API Key (开发用)", type="password")

# --- 5. 侧边栏：激活中心 ---
with st.sidebar:
    st.header("🔑 激活中心")
    user_passcode = st.text_input("在此输入 8 位激活码", placeholder="例如：IELTS888")
    st.divider()
    st.markdown("### 🛒 没有激活码？\n只需 **1元/篇**，即可获得专业批改。")
    st.code("Qwernvvs", language=None)
    st.caption("👆长按微信号复制，加好友买码")

# --- 6. 主界面逻辑 ---
st.title("✍️ 雅思 AI 作文批改系统")

# 初始化 Session State (防止识别后文字因页面刷新消失)
if 'essay_content' not in st.session_state:
    st.session_state.essay_content = ""

# A. 文件上传与 OCR 识别 (已修复之前的非法缩进)
uploaded_file = st.file_uploader("📂 上传作文照片 (支持 JPG/PNG/JPEG)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="已上传的照片", width=300)
    if st.button("🔍 提取照片中的文字"):
        with st.spinner("AI 正在深度识别手写内容..."):
            try:
                # 调用定义好的识图函数
                extracted_text = upload_to_gemini(uploaded_file)
                st.session_state.essay_content = extracted_text
                st.success("识别成功！内容已填入下方文本框。")
            except Exception as e:
                st.error(f"识别出错: {e}")

# B. 文本编辑区 (自动同步 OCR 结果)
essay_text = st.text_area(
    "作文正文 (识别后可在此手动修改):",
    value=st.session_state.essay_content,
    height=350,
    placeholder="在此输入或通过上方照片提取文字..."
)

# C. 验证并执行批改
if st.button("🚀 开始批改并生成报告"):
    valid_keys = load_valid_keys()

    if not user_passcode:
        st.error("❗ 请先输入激活码！")
    elif user_passcode not in valid_keys:
        st.error("❌ 激活码无效。")
    elif not admin_api_key:
        st.error("❗ 未配置 DeepSeek API Key。")
    elif len(essay_text) < 50:
        st.warning("⚠️ 内容太少，请提供更完整的作文。")
    else:
        with st.spinner("🔍 正在连接 DeepSeek 考官大脑..."):
            try:
                # 调用定义好的批改函数
                report = get_ielts_feedback(essay_text, admin_api_key)
                st.success("✅ 批改报告已生成！")
                st.balloons()
                st.markdown("---")
                st.markdown(report)

                # 词汇实验室
                st.header("🏫 雅思高频词汇实验室")
                col1, col2 = st.columns(2)
                words = {"Alleviate": "缓解", "Fluctuate": "波动", "Detrimental": "有害的", "Pros and Cons": "利弊"}
                for i, (w, m) in enumerate(words.items()):
                    with (col1 if i % 2 == 0 else col2):
                        with st.expander(f"📖 {w}"):
                            st.write(f"**中文含义**: {m}")
            except Exception as e:
                st.error(f"❌ 批改失败: {str(e)}")

st.caption("© 2025 雅思 AI 批改助手")