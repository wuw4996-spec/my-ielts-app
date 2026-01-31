# -*- coding:utf-8 -*-
import pytest
import requests
import json


# 假设这是你简历里提到的通用解密逻辑
def decrypt_response(data):
    # 这里模拟你的 AES 解密插件逻辑
    # 实际项目中你会引用：from utils.crypto import AESDecrypt
    return json.loads(data)


class TestPayment:
    """
    支付网关自动化测试类
    演示重点：参数化、Fixture 前后置、断言闭环
    """

    # 1. 使用 Fixture 处理测试前后的数据清理（比如先获取 Token）
    @pytest.fixture(autouse=True)
    def setup_account(self):
        print("\n[Setup] 初始化测试账户，确保余额充足...")
        self.base_url = "https://api.upay.com/v1"
        self.headers = {"Authorization": "Bearer mock_token_123"}
        yield
        print("\n[Teardown] 清理测试订单数据，恢复账户状态...")

    # 2. 使用 parametrize 实现数据驱动（DDT）
    # 模拟不同的货币和金额组合，验证支付接口
    @pytest.mark.parametrize("amount, currency, expected_status", [
        (100, "SGD", "SUCCESS"),
        (50.5, "USD", "SUCCESS"),
        (-1, "CNY", "INVALID_AMOUNT"),  # 边界值测试：负数金额
    ])
    def test_create_payment_order(self, amount, currency, expected_status):
        """测试创建支付订单"""
        payload = {
            "amount": amount,
            "currency": currency,
            "merchant_id": "MCT_001"
        }

        # 发起请求
        response = requests.post(
            f"{self.base_url}/orders",
            json=payload,
            headers=self.headers
        )

        # 3. 处理加密响应（体现你的技术亮点）
        # 很多新手只断言 code，你会断言解密后的业务数据
        if response.status_code == 200:
            raw_data = response.text
            decrypted_data = decrypt_response(raw_data)

            # 断言逻辑
            assert decrypted_data["status"] == expected_status
            if expected_status == "SUCCESS":
                assert decrypted_data["order_id"] is not None
        else:
            # 如果是非 200，验证错误码
            assert response.json()["error_code"] == expected_status

    def test_payment_callback(self):
        """
        测试支付回调（异步逻辑）
        演示重点：JsonPath 思想的应用
        """
        # 模拟 Webhook 回调数据
        callback_json = {
            "event": "payment.captured",
            "data": {
                "object": {
                    "id": "pay_999",
                    "metadata": {"user_id": "wuwei_01"}
                }
            }
        }

        # 像你在简历中写的那样，使用路径提取思想（即使不用库，也要体现这种逻辑）
        order_id = callback_json["data"]["object"]["id"]
        assert order_id == "pay_999"


if __name__ == "__main__":
    # 命令行执行：pytest -vs payment_api_test.py
    pytest.main(["-vs", "payment_api_test.py"])