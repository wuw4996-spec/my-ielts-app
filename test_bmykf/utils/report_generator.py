# -*- coding:utf-8 -*-
import glob
from datetime import datetime
from typing import Dict

from test_bmykf.config.settings import REPORT_DIR, REPORT_TITLE
import json
import os


def generate_html_report(results: list[Dict]):
    """生成HTML测试报告"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file  = REPORT_DIR / f"test_report_{timestamp}.html"

    os.makedirs(REPORT_DIR, exist_ok=True)

    # 简单HTML报告模板
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{REPORT_TITLE}</title>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .pass {{ color: green; }}
            .fail {{ color: red; }}
            .error {{ color: orange; }}
        </style>
    </head>
    <body>
        <h1>{REPORT_TITLE} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>
        {{content}}
    </body>
    </html>
    """

    content = ""
    for channel in results:
        content += f"<h2>渠道: {channel['channel']} - 状态: {channel['status']}</h2>"
        content += "<table><tr><th>测试用例</th><th>结果</th><th>详情</th></tr>"

        for test in channel["details"]:
            status_class = test["result"].lower()
            content += f"""
            <tr>
                <td>{test['test_case']}</td>
                <td class='{status_class}'>{test['result']}</td>
                <td>{test['message']}</td>
            </tr>
            """

        content += "</table><br>"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"测试报告已保存至: {report_file}")
    return report_file