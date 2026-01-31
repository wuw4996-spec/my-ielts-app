import pytest
from test_bmykf.utils.session_manager import SessionManager

@pytest.fixture(scope="function")
def session_manager():
    manager = SessionManager()
    yield manager
    manager.clear_credentials()

@pytest.fixture(scope="function")
def authenticated_session(session_manager):
    """认证会话夹具优化版"""
    for url,params in session_manager.generate_urls("../data/test_links.txt"):
        if session_manager.login_and_get_credentials(url,params):
            yield session_manager
            break
    else:
        pytest.skip("没有可用的测试URL或登录失败")

# @pytest.fixture(scope="function")
# def authenticated_traceid(session_manager):
#     for url,params in session_manager.generate_urls("../data/test_links.txt"):
#         if session_manager.session_manager._get_traceid(url):
#             yield session_manager
#             break
#     else:
#         pytest.skip("没有可用的traceid")
