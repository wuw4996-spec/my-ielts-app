import streamlit as st
from openai import OpenAI
import os
import google.generativeai as genai
from PIL import Image

# --- 1. 页面配置 (必须放在最前面) ---
st.set_page_config(page_title="雅思作文改分王", page_icon="💰")
# --- 初始化 Gemini (识图大脑) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. 注入 CSS 样式 ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stTextArea textarea { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心配置：获取 API Key (修复标红的关键) ---
# 优先从后台 Secrets 读取，如果没有则在侧边栏显示输入框
if "DEEPSEEK_API_KEY" in st.secrets:
    admin_api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    admin_api_key = st.sidebar.text_input("管理员 API Key (开发用)", type="password")


# --- 4. 功能函数：读取卡密 ---
def load_valid_keys():
    file_path = "keys.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("ADMIN123\n")
        return ["ADMIN123"]
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


import google.generativeai as genai
from PIL import Image


def upload_to_gemini(img_file):
    """调用 Gemini API 识别图片文字"""
    # 1. 配置 API Key (从 Secrets 读取)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # 2. 初始化模型
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. 打开图片
    img = Image.open(img_file)

    # 4. 让 AI 提取文字
    prompt = "请精准提取图片中的所有手写或打印文字。直接输出文字内容，不要包含任何多余的解释或说明。"
    response = model.generate_content([prompt, img])

    return response.text

# --- 5. 侧边栏：激活中心与拍照 ---
with st.sidebar:
    st.header("🔑 激活中心")
    user_passcode = st.text_input("在此输入 8 位激活码", placeholder="例如：IELTS888")

    st.divider()

    st.markdown("### 🛒 没有激活码？")
    st.write("只需 **1元/篇**，即可获得专业批改。")
    wechat_id = "Qwernvvs"
    st.code(wechat_id, language=None)
    st.caption("👆长按上方微信号复制，加好友买码")

# --- 6. 主界面：作文输入 (注意：这里退出了 sidebar 缩进) ---
st.title("✍️ 雅思 AI 作文批改系统")
# 将摄像头放在主页面，这样横屏或全屏时框会变大
img_file = st.camera_input("请对准手写作文拍照（确保字迹清晰）")
uploaded_file = st.file_uploader("或者从相册选择照片", type=['png', 'jpg', 'jpeg'])
if img_file:
    # 拍照后，显示一个提取按钮
    if st.button("✨ 提取照片中的文字"):
        with st.spinner("正在识别手写文字..."):
            # 这里调用你之前的 Gemini 识别逻辑
            text = upload_to_gemini(img_file)
            st.session_state.essay_content = text
            st.success("提取成功！文字已自动填入下方输入框。")

st.write("请输入您的雅思作文，AI 将按考官标准进行深度批改。")

# 如果拍照了，这里可以显示识别结果（目前先留空让用户贴，或后续接 OCR）
essay_content = st.text_area("作文正文:", height=350, placeholder="In terms of the table...")

if st.button("🚀 开始批改并生成范文"):
    # 逻辑检查
    valid_keys = load_valid_keys()

    if not user_passcode:
        st.error("❗ 请先输入激活码！")
    elif user_passcode not in valid_keys:
        st.error("❌ 激活码无效。请联系客服购买。")
    elif not admin_api_key:
        st.error("❗ 管理员未配置 API Key。")
    elif len(essay_content) < 100:
        st.warning("⚠️ 作文内容过短，无法精准评分。")
    else:
        with st.spinner("🔍 正在连接 DeepSeek 考官大脑..."):
            try:
                client = OpenAI(api_key=admin_api_key, base_url="https://api.deepseek.com")

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

                # 展示结果
                st.success("✅ 批改报告已生成！")
                st.balloons()
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

                # 词汇实验室展示
                st.header("🏫 雅思高频词汇实验室")
                col1, col2 = st.columns(2)
                words = {"Alleviate": "缓解", "Fluctuate": "波动", "Detrimental": "有害的", "Pros and Cons": "利弊"}
                for i, (w, m) in enumerate(words.items()):
                    with (col1 if i % 2 == 0 else col2):
                        with st.expander(f"📖 {w}"):
                            st.write(m)

            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")

st.caption("© 2025 雅思 AI 批改助手")