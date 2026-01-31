# -*- coding:utf-8 -*-
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent
CHANNEL_URLS_FILE = BASE_DIR / "data" / "test_link.txt"
REPORT_DIR = BASE_DIR / "reports"

# 测试配置
TEST_CASES = [
    "tests.test_cases.test_profile",
    "tests.test_cases.test_order",
    # 添加更多测试模块...
]

# 报告配置
REPORT_TITLE = "渠道接口测试报告"