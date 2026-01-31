import pytest
from openai import OpenAI

# --- 待测逻辑（实际开发中可以从主程序导入） ---
# 这里的 VALID_KEYS 必须和主程序保持一致
VALID_KEYS = ["IELTS666", "SUCCEED2025", "MEMBER888"]


def verify_passcode(code):
    if code in VALID_KEYS:
        return True
    return False


def call_ai_api(api_key, essay_text):
    if not api_key:
        raise ValueError("API Key 缺失")

    # 建立一个临时的客户端测试连通性
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5  # 节省 Token，只测连通性
    )
    return response.status_code if hasattr(response, 'status_code') else 200


# --- Pytest 测试用例 ---

# 测试 A: 卡密验证功能
@pytest.mark.parametrize("input_code, expected", [
    ("IELTS666", True),  # 正确卡密
    ("WRONG123", False),  # 错误卡密
    ("", False),  # 空输入
])
def test_passcode_logic(input_code, expected):
    assert verify_passcode(input_code) == expected


# 测试 B: API 密钥安全性测试
def test_ai_api_no_key():
    with pytest.raises(ValueError, match="API Key 缺失"):
        call_ai_api(None, "Test essay")


# 测试 C: 模拟 API 调用（集成测试）
# 注意：运行这个测试会消耗极微量的 DeepSeek 余额
def test_api_connectivity():
    # 这里填入你申请到的真实 sk-xxxx
    real_api_key = "sk-0a1570b1d36f49be834e118eb1ebefeb"

    # 如果你还没申请到 Key，可以先跳过这个测试
    if real_api_key == "你的_DEEPSEEK_API_KEY":
        pytest.skip("未配置真实的 API Key，跳过连通性测试")

    status = call_ai_api(real_api_key, "Test")
    assert status == 200
# -*- coding:utf-8 -*-
