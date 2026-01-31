import streamlit as st
from openai import OpenAI  # DeepSeek 使用兼容 OpenAI 的库

# 1. 页面配置
st.set_page_config(page_title="IELTS AI Mentor", page_icon="✍️")
st.title("✍️ 雅思 AI 作文批改助手 (DeepSeek 版)")
st.subheader("专业考官级评分，助你攻克雅思")

# 2. 侧边栏设置
with st.sidebar:
    st.header("配置中心")
    # 让用户输入自己的 Key
    api_key = st.text_input("输入 DeepSeek API Key", type="password", help="从 platform.deepseek.com 获取")
    st.markdown("[点击这里获取 Key](https://platform.deepseek.com/)")

# 3. 作文输入区
essay_text = st.text_area("在此粘贴你的雅思作文 (Task 1 或 Task 2):", height=300, placeholder="In many countries...")

if st.button("🚀 开始极速批改"):
    if not api_key:
        st.error("❌ 请先在左侧输入 API Key！")
    elif len(essay_text) < 50:
        st.warning("⚠️ 作文太短了，请输入完整的作文。")
    else:
        with st.spinner("🔍 考官正在深度阅卷并生成范文..."):
            try:
                # 4. DeepSeek 专属配置
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"  # 这是关键：指向 DeepSeek 服务器
                )

                prompt = f"""你是一位资深的雅思前考官。请根据雅思考试的四个官方维度：
                1. Task Response (任务完成度)
                2. Coherence and Cohesion (连贯与衔接)
                3. Lexical Resource (词汇丰富度)
                4. Grammatical Range and Accuracy (语法多样性及准确性)

                请对下文进行批改。返回格式要求：
                ### 1. 预计分数 (Band Score)
                ### 2. 详细点评 (Detailed Feedback)
                ### 3. 词汇与语法升级 (Vocabulary & Grammar Boost)
                ### 4. 满分范文 (Band 9 Sample Answer)

                文章内容如下：
                {essay_text}"""

                response = client.chat.completions.create(
                    model="deepseek-chat",  # 使用 DeepSeek 的聊天模型
                    messages=[
                        {"role": "system", "content": "你是一个专业的雅思作文批改专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )

                # 5. 显示结果
                st.success("✅ 批改完成！")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"发生错误: {str(e)}")

# 6. 页脚
st.markdown("---")
st.caption("提示：雅思作文批改建议仅供参考。继续学习 pytest 可以让你的 App 更稳定！")
# -*- coding:utf-8 -*-
