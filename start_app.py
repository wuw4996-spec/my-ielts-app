from playwright.sync_api import sync_playwright


def my_login():
    with sync_playwright() as p:
        # headless=False 让你能看到过程，slow_mo 慢动作 1 秒
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()

        print("正在打开百度...")
        page.goto("https://www.baidu.com")

        # 稳妥起见，填入并回车
        page.fill("#kw", "Playwright Python")
        page.press("#kw", "Enter")

        # 截图留个念想
        page.screenshot(path="result.png")
        print("执行完毕，截图已保存。")

        browser.close()


if __name__ == "__main__":
    my_login()