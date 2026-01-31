from pathlib import Path
from typing import List
from utils.test_runner import TestRunner
from utils.report_generator import generate_html_report
from config.settings import CHANNEL_URLS_FILE


def load_channel_urls() -> list[str]:
    """从文件加载渠道URL"""
    with open(CHANNEL_URLS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    # 加载渠道URL
    channel_urls = load_channel_urls()
    print(f"发现 {len(channel_urls)} 个渠道需要测试")

    # 执行测试
    runner = TestRunner()
    runner.run_all_channels(channel_urls)

    # 生成报告
    report_path = generate_html_report(runner.test_results)

    print(f"测试完成，报告已生成: {report_path}")


if __name__ == "__main__":
    main()