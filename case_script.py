# -*- coding:utf-8 -*-
import re
import time
from asyncio import sleep
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests


def _cookie_and_trace_id_flow():
    """获取traceId"""
    with open('D:/pythonProject/test_links.txt', mode='r', encoding='UTF-8') as f:
        info = f.readlines()
        urls = []
        for i in info:
            # i = '张三  2587.98\n'z
            # i.strip() = '张三  2587.98'
            # i.strip().split() = ['张三', '2587.98']
            parts = re.split(r'\s+', i.strip())
            if parts and parts[-1].startswith('http'):
                urls.append(parts[-1])
    print(urls)

    # 遍历每个渠道获取cookie和trace
    for link in urls:

        # # 将Cookie转换为requests可用的格式
        # requests_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        # print(requests_cookies)


        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        data = {"channelId": query_params.get("channelId", [""])[0],
                "funcflag": '',
                "htmlVersion": '2',
                "phoneNum": query_params.get("msisdn", [""])[0],
                "serviceType": "1"+ query_params.get("servicetype", [""])[0],
                "terminalBrand": '其他',
                "terminalOS": "Windows 10",
                "terminalType":"2",
                "userId": query_params.get("userId", [""])[0],}
        print(data)

        # 创建会话对象
        session = requests.Session()
        # 发送登录POST请求
        login_response = session.post(link, json=data)
        print(login_response.text)
        # 查看会话中的所有Cookie
        print("当前会话Cookies:", session.cookies.get_dict())

        #获取traceid值
        url1 = "http://112.25.126.97:8380/ocmservice/api/v1/channel/userBehaviorTrackBegin"
        data1 = {"serviceType": "1"+ query_params.get("servicetype", [""])[0],
                "channelId": query_params.get("channelId", [""])[0],
                "telNumber": query_params.get("msisdn", [""])[0],
                "userId": query_params.get("userId", [""])[0],
                "terminalIp": query_params.get("appid", [""])[0],  # 示例默认值，可根据需要修改
                'beginTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        # 后续请求会自动携带Cookie
        profile_response = session.post(url1,json=data)
        print("受保护页面:", profile_response.text)
        res= profile_response.json()
        traceId = res['responseInfo']['traceId']
        print(traceId)
        time.sleep(3)
        #测试第一个输入接口
        test_url1="http://112.25.126.97:8380/faqservice/api/v1/channel/bot/queryKngByKey"
        test_data1= {"channelId": query_params.get("channelId", [""])[0],
               "qaHis":[],
               "queryString":"你好",
               "rejectionNum":0,
                "telNumber": query_params.get("msisdn", [""])[0],
               "trackSession":traceId,
                "userId": query_params.get("userId", [""])[0]}
        test1_response = session.post(test_url1,json=test_data1)
        test_res1 = test1_response.json()['result']["resultDes"]

        print(f"第一个测试:发送你好接口；接口响应为{test_res1}")
        #测试查看历史记录接口
        test_url2="http://112.25.126.97:8380/ocmservice/api/v1/channel/queryChatRecordHis"
        # 获取当前时间戳（秒级，含小数部分）
        timestamp_seconds = time.time()

        # 转换为毫秒级（整数）
        endTime = int(timestamp_seconds * 1000)
        test_data2= {"channelId": query_params.get("channelId", [""])[0],
               "endTime":endTime,
                "pageNo": 1,
               "pageSize":10,
                "userId": query_params.get("userId", [""])[0]}
        test2_response = session.post(test_url2,json=test_data2)
        test_res2 = test2_response.json()['result']["resultDes"]

        print(f"第二个测试:查看历史记录接口；接口响应为{test_res2}")


_cookie_and_trace_id_flow()