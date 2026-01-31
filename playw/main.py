import os
import csv
import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import requests
import json
# 1. 加载配置
load_dotenv()


def get_baidu_hot_search():
    with sync_playwright() as p:
        # 百度电脑版很稳定，不需要模拟手机，直接启动即可
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()

        # 2. 准备文件夹
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # 如果 .env 读不到，就用默认值 'reports'
        report_base = os.getenv('REPORT_DIR') or "reports"
        save_dir = os.path.join(report_base, today)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 3. 访问百度热搜
        url = os.getenv('TARGET_URL') or "https://top.baidu.com/board?tab=realtime"
        print(f"🚀 正在前往: {url}")

        try:
            page.goto(url, timeout=30000)
            # 等待热搜标题元素出现 (百度热搜的标题类名通常包含 c-single-text-ellipsis)
            page.wait_for_selector(".c-single-text-ellipsis", timeout=10000)
        except Exception as e:
            print(f"❌ 访问失败或超时: {e}")
            page.screenshot(path="error_debug.png")
            return

        # 4. 抓取前 10 条 (适配百度最新的结构)
        hot_list = []

        # 抓取所有的行
        items = page.query_selector_all(".category-wrap_i8Z9D")[:10]

        # 如果上面的不行，试试这个更通用的方案：
        if not items:
            items = page.query_selector_all("main div a")  # 尝试找正文里的链接

        print(f"找到条目数量: {len(items)}")

        for index, item in enumerate(items):
            # 百度热搜标题通常在 c-single-text-ellipsis 类中
            title_el = item.query_selector(".c-single-text-ellipsis")
            # 热度值通常在 hot-index 相关的类中
            score_el = item.query_selector(".hot-index_1_1Ex")

            if title_el:
                title = title_el.inner_text().strip()
                score = score_el.inner_text().strip() if score_el else "N/A"
                print(f"抓取到第 {index + 1} 条: {title}")  # 实时打印，方便调试
                hot_list.append({"排名": index + 1, "热搜话题": title, "热度": score})

        # 尝试寻找包含“热指数”或纯数字的文本
        full_text = item.inner_text()
        # 简单的逻辑：如果文本里有“万”或者很大的数字，通常就是热度
        import re
        scores = re.findall(r'\d+', full_text)  # 找数字
        score = scores[-1] if scores else "N/A"  # 取最后一个数字通常是热度
        # 5. 保存 CSV
        csv_path = os.path.join(save_dir, "baidu_hot.csv")

        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["排名", "热搜话题", "热度"])
            writer.writeheader()
            writer.writerows(hot_list)



        # 6. 截图
        page.screenshot(path=os.path.join(save_dir, "baidu_view.png"))
        print(f"✅ 大功告成！文件已存至: {save_dir}")

        browser.close()

def send_notification(content):
    # 这里以钉钉机器人为例，你需要先在钉钉群获取 Webhook 地址
    webhook_url = "你的钉钉机器人WEBHOOK地址"
    headers = {"Content-Type": "application/json"}
    message = {
        "msgtype": "text",
        "text": {
            "content": f"📢 情报官汇报：今日百度热搜已更新！\n\n{content}\n\n详情请查看本地报表。"
        }
    }
    requests.post(webhook_url, data=json.dumps(message), headers=headers)

# 在你原本代码的保存 CSV 逻辑之后调用：
report_text = "\n".join([f"{item['排名']}. {item['热搜话题']}" for item in hot_list[:5]])
send_notification(report_text)


if __name__ == "__main__":
    get_baidu_hot_search()