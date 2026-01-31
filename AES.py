# -*- coding:utf-8 -*-
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCrypto:
    def __init__(self, key, iv):
        self.key = key.encode('utf-8')  # 密钥：必须是16, 24, 或 32 字节
        self.iv = iv.encode('utf-8')    # 偏移量：CBC模式需要16字节

    def encrypt(self, data):
        """加密方法"""
        # 1. 创建加密器，选择 CBC 模式
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 2. 对明文进行填充（AES要求块大小必须是16字节的倍数）
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        # 3. 将结果转为 Base64 方便在接口中传输
        return base64.b64encode(ct_bytes).decode('utf-8')

    def decrypt(self, text):
        """解密方法"""
        # 1. Base64 解码
        data = base64.b64decode(text)
        # 2. 创建解密器
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 3. 解密并去除填充，得到原始明文
        return unpad(cipher.decrypt(data), AES.block_size).decode('utf-8')

# --- 模拟面试场景演示 ---
if __name__ == "__main__":
    my_key = "1234567812345678"  # 16位密钥
    my_iv = "8765432187654321"   # 16位偏移量
    crypto = AESCrypto(my_key, my_iv)

    # 模拟接口返回的加密数据
    secret_data = crypto.encrypt("成都测开面试必过")
    print(f"加密后的乱码: {secret_data}")

    # 模拟自动化脚本中的解密断言
    original_data = crypto.decrypt(secret_data)
    print(f"解密后的明文: {original_data}")