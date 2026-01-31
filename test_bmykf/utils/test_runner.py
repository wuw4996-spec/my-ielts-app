# -*- coding:utf-8 -*-
import datetime
import importlib
import requests
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Tuple
from test_bmykf.config.settings import TEST_CASES


class TestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.traceid = None
        self.test_results = []

    def process_channel_url(self, url: str) -> Tuple[Dict, str]:
        """解析渠道URL获取参数和基础URL"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        params = parse_qs(parsed.query)
        return {k: v[0] for k, v in params.items()}, base_url

    def login_and_get_traceid(self, login_url: str, login_params: Dict) -> bool:
        """登录并获取traceid"""
        try:
            # 登录请求
            parsed_url = urlparse(login_url)
            query_params = parse_qs(parsed_url.query)

            data = {"channelId": query_params.get("channelId", [""])[0],
                    "funcflag": '',
                    "htmlVersion": '2',
                    "phoneNum": query_params.get("msisdn", [""])[0],
                    "serviceType": "1" + query_params.get("servicetype", [""])[0],
                    "terminalBrand": '其他',
                    "terminalOS": "Windows 10",
                    "terminalType": "2",
                    "userId": query_params.get("userId", [""])[0], }
            response = self.session.post(login_url, json=login_params)
            if response.status_code != 200:
                return False

            # 获取traceid
            url1 = "http://112.25.126.97:8380/ocmservice/api/v1/channel/userBehaviorTrackBegin"
            data1 = {"serviceType": "1" + query_params.get("servicetype", [""])[0],
                     "channelId": query_params.get("channelId", [""])[0],
                     "telNumber": query_params.get("msisdn", [""])[0],
                     "userId": query_params.get("userId", [""])[0],
                     "terminalIp": query_params.get("appid", [""])[0],  # 示例默认值，可根据需要修改
                     'beginTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            trace_response = self.session.post(url1,data1)
            self.traceid = trace_response.json().get("traceid")
            return True
        except Exception:
            return False

    def run_tests_for_channel(self, channel_url: str) -> Dict:
        """为单个渠道执行所有测试用例"""
        channel_params, base_url = self.process_channel_url(channel_url)
        channel_name = urlparse(channel_url).path.split("/")[1]

        if not self.login_and_get_traceid(channel_url, channel_params):
            return {
                "channel": channel_name,
                "status": "登录失败",
                "details": []
            }

        test_details = []
        for test_module in TEST_CASES:
            module = importlib.import_module(test_module)
            test_func = getattr(module, "run_test", None)
            if test_func:
                result = test_func(self.session, base_url, self.traceid)
                test_details.append({
                    "test_case": test_module.split(".")[-1],
                    "result": result["status"],
                    "message": result.get("message", "")
                })

        return {
            "channel": channel_name,
            "status": "完成",
            "details": test_details
        }

    def run_all_channels(self, channel_urls: List[str]):
        """执行所有渠道测试"""
        for url in channel_urls:
            channel_result = self.run_tests_for_channel(url)
            self.test_results.append(channel_result)
            self.session.cookies.clear()  # 清理当前渠道的cookies