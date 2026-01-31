# -*- coding:utf-8 -*-
import datetime
import re
import requests
from urllib.parse import urlparse, parse_qs


class SessionManager:
    def __init__(self):
        self.current_session = requests.Session()
        self.traceid = None
        self.processed_urls = set()  # 记录已处理的URL
        self.current_params = {} # 存储当前URL的参数

    def generate_urls(self,file_path):
        """读取输入文件并构建URL"""
        with open(file_path, mode='r', encoding='UTF-8') as f:
            full_url = []
            for line in f:
                parts = re.split(r'\s+', line.strip())
                if parts and parts[-1].startswith('http'):
                    full_url.append(parts[-1])
                    # 解析查询参数
            for i in full_url:
                parsed = urlparse(i)
                params = parse_qs(parsed.query)
                yield full_url, params


            # info = f.readlines()
            # full_url = []
            # for i in info:
            #     # i = '张三  2587.98\n'
            #     # i.strip() = '张三  2587.98'
            #     # i.strip().split() = ['张三', '2587.98']
            #     parts = re.split(r'\s+', i.strip())
            #     if parts and parts[-1].startswith('http'):
            #         full_url.append(parts[-1])
            #         # 解析查询参数
            #         print(full_url)
            #         yield full_url

    def login_and_get_credentials(self, url,params):
        """通过POST请求登录并获取凭证"""
        print(f"单链接:{url}")
        for i in url:
            if i in self.processed_urls:
                return False

            parsed_url = urlparse(i)
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
            print(f"单链接:{url}")
            # 发送POST登录请求
            login_response = requests.post(i, json=data)

            if login_response.status_code == 200:
                self.current_params = params
                self.processed_urls.add(i)
                return True
            return False

    def _get_traceid(self,url):
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            url1 = "http://112.25.126.97:8380/ocmservice/api/v1/channel/userBehaviorTrackBegin"
            data1 = {"serviceType": "1" + query_params.get("servicetype", [""])[0],
                     "channelId": query_params.get("channelId", [""])[0],
                     "telNumber": query_params.get("msisdn", [""])[0],
                     "userId": query_params.get("userId", [""])[0],
                     "terminalIp": query_params.get("appid", [""])[0],
                     # 示例默认值，可根据需要修改
                     'beginTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            # 后续请求会自动携带Cookie
            trace_response = self.current_session.post(url1, json=data1)
            return trace_response.json().get("traceid")
        except Exception as e:
            print(f"获取 {url} 的凭证失败: {str(e)}")
            return None

    def get_cookies(self):
        """获取当前会话的cookies"""
        return self.session.cookies.get_dict()

    def get_current_params(self):
        """获取当前URL的参数"""
        print("current_params:", self.current_params)
        return {k: v[0] for k, v in self.current_params.items()}

    def clear_credentials(self):
        """清理当前凭证"""
        if self.current_session:
            self.current_session.close()
        self.current_session = None
        self.traceid = None
        self.current_params = {}