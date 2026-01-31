from playwright.sync_api import sync_playwright
import os


def login_and_save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # 这里的 storage_state 是关键
        # 如果 auth.json 存在，就加载它；否则就创建一个空的环境
        auth_file = "auth.json"

        if os.path.exists(auth_file):
            print("🔑 发现通行证，正在免登进入...")
            context = browser.new_context(storage_state=auth_file)
        else:
            print("🆕 没发现通行证，请手动登录一次...")
            context = browser.new_context()

        page = context.new_page()
        # 以百度或某个你常去的网站为例
        page.goto("https://www.baidu.com")

        # --- 逻辑判断 ---
        if not os.path.exists(auth_file):
            # 如果是第一次运行，程序会停在这里等你手动输入账号登录
            print("请在浏览器窗口完成登录，登录成功后回到这里按回车...")
            input("确认登录成功后，请按回车键保存状态并退出：")

            # 登录成功后，保存所有 Cookie 到文件
            context.storage_state(path=auth_file)
            print(f"✅ 通行证已保存至 {auth_file}")
        else:
            print("🚀 已跳过登录，直接进入主页！")
            # 可以在这里写你登录后才能做的抓取逻辑
            page.screenshot(path="logged_in_check.png")

        browser.close()


if __name__ == "__main__":
    login_and_save_session()