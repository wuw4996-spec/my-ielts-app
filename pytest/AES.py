# -*- coding:utf-8 -*-
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64



def decrypt_payment_data(encrypted_text, key, iv):
    # 1. Base64 解码
    encrypted_bytes = base64.b64decode(encrypted_text)

    # 2. 初始化 AES 对象 (使用 CBC 模式)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))

    # 3. 解密并去除填充 (Padding)
    decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)

    return decrypted_bytes.decode('utf-8')


# 实际测试用例中的用法
def test_balance_inquiry():
    response = requests.post(url, data=payload)
    # 假设返回的是 {"data": "AbC123xyz..."}
    encrypted_data = response.json()['data']

    # 调用你写的插件
    real_data = decrypt_payment_data(encrypted_data, "my_secret_key_16", "random_iv_16_char")

    # 进行断言
    assert "balance" in real_data
    assert float(json.loads(real_data)['balance']) >= 0