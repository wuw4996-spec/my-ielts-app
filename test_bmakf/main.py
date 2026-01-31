from urllib.parse import urlparse, parse_qs

from case_script import test_cookie_and_trace_id_flow


class case:
    def __init__(self):
        self.ct = (None, None, None)

    def case1(self):
        result = test_cookie_and_trace_id_flow()
        if self.ct is None:
            raise ValueError("self.ct 未被正确初始化，请先调用初始化方法")

        link, session, traceId = self.ct  # 安全解包
        print(f"self.ct 的值: {self.ct}, 类型: {type(self.ct)}")
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        url = "http://112.25.126.97:8380/ocmservice/api/v1/channel/queryChatRecordHis"
        data = {"qaHis": [],
                "trackSession": traceId,
                "channelId": query_params.get("channelId", [""])[0],
                "telNumber": query_params.get("msisdn", [""])[0],
                "userId": query_params.get("userId", [""])[0],
                "queryString": "你好",
                "rejectionNum": 0}
        print(data)
        # 发送登录POST请求
        login_response = session.post(url, json=data)
        print(login_response.json())

if __name__ == "__main__":
    gener = case()
    print(gener.case1())