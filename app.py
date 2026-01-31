# -*- coding:utf-8 -*-
import streamlit as st
import openai

# 1. 页面配置
st.set_page_config(page_title="IELTS AI Mentor", page_icon="✍️")
st.title("✍️ 雅思 AI 作文批改助手")
st.subheader("输入你的作文，获取专业考官级评分")

# 2. 侧边栏设置 (可以填入你的 OpenAI Key)
with st.sidebar:
    api_key = st.text_input("输入 OpenAI API Key", type="password")
    model = st.selectbox("选择模型", ["gpt-3.5-turbo", "gpt-4"])

# 3. 作文输入区
essay_text = st.text_area("在此粘贴你的雅思作文 (Task 1 或 Task 2):", height=300)

if st.button("开始批改"):
    if not api_key:
        st.error("请先在左侧输入 API Key！")
    elif len(essay_text) < 50:
        st.warning("作文太短了，请输入完整的段落。")
    else:
        with st.spinner("考官正在阅卷中，请稍候..."):
            try:
                # 4. AI 批改逻辑
                client = openai.OpenAI(api_key=api_key)
                prompt = f"""你是一位资深的雅思前考官。请根据雅思考试的四个官方维度（任务完成度、连贯性、词汇量、语法）批改以下文章。
                请给出：
                1. 预计总分
                2. 四项维度的分项点评
                3. 改进建议
                4. 一个范文版本（Band 9）
                文章内容如下：\n\n{essay_text}"""

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": "你是一个专业的雅思作文批改专家。"},
                              {"role": "user", "content": prompt}]
                )

                # 5. 显示结果
                st.success("批改完成！")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"发生错误: {e}")

# 6. 页脚
st.markdown("---")
st.caption("© 2025 IELTS AI Mentor - 你的赚钱原型机")