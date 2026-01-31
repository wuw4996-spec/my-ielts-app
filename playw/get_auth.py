# -*- coding:utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 记得 headless=False，不然你没法手动操作
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(**p.devices['iPhone 13'])
    page = context.new_page()

    # 访问微博登录页
    page.goto("https://passport.weibo.cn/signin/login")

    print("👋 请在浏览器中完成登录...")
    # 只要登录成功，页面会自动跳转到首页或个人页
    # 此时在 PyCharm 控制台按回车
    input("登录成功后请按回车保存 Cookie：")

    # 保存状态到 auth.json
    context.storage_state(path="auth.json")
    print("✅ 成功！通行证已保存为 auth.json")
    browser.close()