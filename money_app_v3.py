import streamlit as st
from openai import OpenAI
import os


# 在 st.title 之后增加

st.markdown("""
    <style>
    /* 让按钮变成吸睛的亮橙色 */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border: none;
    }
    /* 适配手机端的文字大小 */
    .stTextArea textarea {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
    user_passcode = st.text_input("在此输入 8 位激活码", placeholder="例如：IELTS888")
    
    st.divider()
    
    # 重点：购买引导
    st.markdown("### 🛒 没有激活码？")
    st.write("只需 **1元/篇**，即可获得全维度批改 + 满分范文。")
    
    # 增加一个点击复制的体验（利用简单的 markdown）
    wechat_id = "Qwernvvs" # 换成你的微信
    st.code(wechat_id, language=None)
    st.caption("👆长按上方微信号复制，加好友买码")
    
    if st.button("查看购买流程"):
        st.info("1. 加微信 -> 2. 转账 -> 3. 自动/手动发码 -> 4. 粘贴批改")

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

                prompt = f"""你是一位严格的雅思写作前考官。请对以下作文进行专业测评。
                内容如下：{essay_content}
                
                请严格按以下模块输出（使用 Markdown 格式）：
                
                ## 📊 测评成绩单
                - **Overall Band Score: [分数]**
                - Task Response: [分数]
                - Coherence and Cohesion: [分数]
                - Lexical Resource: [分数]
                - Grammatical Range and Accuracy: [分数]
                
                ---
                ## 📝 考官详细批改 (Detailed Feedback)
                > 指出文章中最严重的 3 个逻辑或语法错误，并给出修改方案。
                
                ---
                ## 💡 词汇与表达升级
                - **初级表达**: [原文中的词] -> **高级替换**: [推荐词汇]
                - **亮点句型**: [推荐一个适合本文的复杂句式]
                
                ---
                ## 🏆 满分范文 (Band 9 Sample)
                [请针对该题目写一篇高分示范]
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





