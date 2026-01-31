from typing import Dict
from urllib.parse import urlparse, parse_qs


def run_test(session, base_url, traceid) -> Dict:
    """测试获取用户信息"""
    try:
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)

        url = "http://112.25.126.97:8380/ocmservice/api/v1/channel/queryChatRecordHis"
        data = {"qaHis":[],
                "trackSession":traceid,
                "channelId":query_params.get("channelId", [""])[0],
                "telNumber":query_params.get("msisdn", [""])[0],
                "userId":query_params.get("userId", [""])[0],
                "queryString":"你好",
                "rejectionNum":0}
        print(data)
        # 发送请求
        response = session.post(url,json=data)
        print(response.json())
        # 验证响应
        assert response.status_code == 200
        assert "username" in response.json()
        return {"status": "通过", "message": ""}

    except AssertionError as e:
        return {"status": "失败", "message": str(e)}
    except Exception as e:
        return {"status": "错误", "message": str(e)}


# def test_submit_with_params(authenticated_session):
#     """测试提交带参数的请求"""
#     sm = authenticated_session
#     params = sm.get_current_params()
#
#     # 构建负载，使用URL中的参数
#     payload = {
#         "user": params["user"],
#         "token": params["token"],
#         "traceid": sm.traceid,
#         "action": "test_submit"
#     }
#
#     # 发送请求
#     response = sm.current_session.post(
#         f"{BASE_URL}{API_PATHS['submit']}",
#         json=payload
#     )
#
#     # 验证响应
#     assert response.status_code == 201
#     assert response.json().get("status") == "success"