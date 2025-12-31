import streamlit as st
from openai import OpenAI
import os


# --- 功能函数：读取卡密文件 ---
def load_valid_keys():
    file_path = "keys.txt"
    if not os.path.exists(file_path):
        # 如果文件不存在，创建一个默认的
        with open(file_path, "w") as f:
            f.write("ADMIN123\n")
        return ["ADMIN123"]

    with open(file_path, "r", encoding="utf-8") as f:
        # 读取每一行，去掉空格和换行
        return [line.strip() for line in f.readlines() if line.strip()]


# --- 页面 UI 配置 ---
st.set_page_config(page_title="雅思作文改分王", page_icon="💰")
st.title("✍️ 雅思 AI 作文批改系统")

# 侧边栏：管理与支付
with st.sidebar:
    st.header("🔑 激活中心")
    user_passcode = st.text_input("输入您的激活码", type="password", help="激活码可从客服处购买")

    st.divider()

    st.header("⚙️ 配置中心")
    # 为了方便你测试，这里保留 Key 输入框；以后你可以直接写在代码里隐藏
    admin_api_key = st.text_input("管理员 API Key", type="password")

    st.divider()
    st.markdown("### 🛒 购买激活码")
    st.write("1元/次，即买即用")
    st.info("联系微信号: `Qwernvvs` (备注: 买码)")
    # st.image("wx_pay_qr.png") # 取消注释可以上传收款码图片

# 主界面：作文输入
st.write("请输入您的雅思作文，AI 将按考官标准进行深度批改。")
essay_content = st.text_area("作文正文:", height=350, placeholder="In terms of the table...")

if st.button("🚀 开始批改并生成范文"):
    # 1. 验证激活码
    valid_keys = load_valid_keys()

    if not user_passcode:
        st.error("❗ 请先输入激活码！")
    elif user_passcode not in valid_keys:
        st.error("❌ 激活码无效或已被使用。请联系客服购买新码。")

    # 2. 验证 API Key
    elif not admin_api_key:
        st.error("❗ 管理员未配置 API Key。")

    # 3. 验证作文内容
    elif len(essay_content) < 100:
        st.warning("⚠️ 作文内容过短，请确保输入完整的雅思作文。")

    else:
        # 4. 执行 AI 批改
        with st.spinner("🔍 正在连接 DeepSeek 考官大脑，请稍候..."):
            try:
                client = OpenAI(api_key=admin_api_key, base_url="https://api.deepseek.com")

                prompt = f"""你是一位雅思资深考官。请对以下作文进行专业批改。
                内容：{essay_content}

                要求格式：
                1. [Score] 给出总分和各项小分。
                2. [Analysis] 针对 TR, CC, LR, GRA 四个维度详细点评。
                3. [Suggestions] 指出文章中 3 个可以改进的具体地方。
                4. [Sample] 提供一个 Band 9 的高分范文。
                """

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个专业的雅思作文批改专家，严谨且专业。"},
                        {"role": "user", "content": prompt}
                    ]
                )

                # 成功展示
                st.success("✅ 批改报告已生成！")
                st.balloons()
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"❌ 批改失败，原因: {str(e)}")

# 页脚
st.caption("© 2025 雅思 AI 批改助手 | 稳定的自动化测试由 Pytest 提供支持")
# -*- coding:utf-8 -*-

