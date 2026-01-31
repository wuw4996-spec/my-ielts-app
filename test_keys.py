# -*- coding:utf-8 -*-
# test_keys.py
import os
import pytest
from money_app_v3 import load_valid_keys


def test_load_keys_from_file():
    # 1. 准备测试数据：临时创建一个 keys.txt
    test_keys = "TEST123\nTEST456"
    with open("keys.txt", "w") as f:
        f.write(test_keys)

    # 2. 调用函数
    keys = load_valid_keys()

    # 3. 断言验证
    assert "TEST123" in keys
    assert "TEST456" in keys
    assert len(keys) == 2


def test_file_not_found_fallback():
    # 删掉 keys.txt 看看程序会不会崩
    if os.path.exists("keys.txt"):
        os.remove("keys.txt")

    keys = load_valid_keys()
    assert "ADMIN123" in keys  # 确保有默认值