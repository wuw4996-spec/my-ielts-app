import pytest
def test_app():
    print("hello")
    date_str = "2026/01/05"
    # 1. 先用 split 把斜杠切开
    parts = date_str.split("/")  # 得到 ['2026', '01', '05']
    # 2. 再用 join 用横线连起来
    new_date = "-".join(parts)  # 得到 "2026-01-05"
    print(new_date)
    assert 1==1