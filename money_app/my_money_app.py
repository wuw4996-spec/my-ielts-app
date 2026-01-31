import streamlit as st
from openai import OpenAI

# --- 赚钱核心：定义的卡密池 (实际开发中可以放进数据库或文件) ---
# 你可以把这些码卖给学生，比如 5 元一个
VALID_KEYS = ["IELTS666", "SUCCEED2025", "MEMBER888"]

st.set_page_config(page_title="雅思作文改分王", page_icon="💰")
st.title("✍️ 雅思 AI 作文批改 (付费版)")

# 侧边栏配置
with st.sidebar:
    st.header("🔑 激活与配置")
    user_passcode = st.text_input("输入你的激活码/充值码", type="password")

    # 你的 API Key (为了安全，建议直接写在环境变量里，或者这里让管理员输入)
    admin_api_key = st.text_input("API Key (管理员配置)", type="password")

    st.markdown("---")
    st.markdown("### 🛒 如何获取激活码？")
    st.info("扫描下方二维码或联系微信: `your_wechat` 购买 (1元/次)")
    # st.image("your_qr_code.png") # 这里可以放你的收款码

# 主界面
essay_text = st.text_area("在此粘贴你的作文:", height=300)

if st.button("开始批改"):
    # 1. 验证卡密
    if user_passcode not in VALID_KEYS:
        st.error("❌ 激活码无效或已过期，请联系管理员购买！")

    # 2. 验证 API Key
    elif not admin_api_key:
        st.error("❌ 管理员未配置 API 接口。")

    # 3. 验证输入内容
    elif len(essay_text) < 50:
        st.warning("⚠️ 作文太短。")

    else:
        with st.spinner("💰 正在消耗点数并进行深度批改..."):
            try:
                client = OpenAI(api_key=admin_api_key, base_url="https://api.deepseek.com")

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一位雅思考官。"},
                        {"role": "user", "content": f"请批改并打分：\n{essay_text}"}
                    ]
                )

                st.success("✅ 批改成功！")
                st.markdown(response.choices[0].message.content)

                # 提示用户：如果想再改一篇，需要新码（或者你可以做点数扣除逻辑）
                st.balloons()

            except Exception as e:
                st.error(f"出错啦: {e}")
# -*- coding:utf-8 -*-
