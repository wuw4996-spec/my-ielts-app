# -*- coding:utf-8 -*-
import json
import openpyxl
import hashlib
import time
import random
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse, quote


class URLGenerator:

    def __init__(self):
        self.generated_urls = []

    def generate_md5_hash(self, params):
        """根据签名机制生成MD5 hash值"""
        # 过滤空值参数并转换为字符串
        self.BK = str(params['bk'])
        print(type(self.BK))
        exclude_fields = {"bk"}  # 需要排除的字段集合

        filtered_params = {
            k: str(v) for k, v in params.items()
            if v is not None
               and str(v).strip() != ''
               and k not in exclude_fields  # 新增条件：排除指定字段
        }

        # 按键名排序
        sorted_params = OrderedDict(sorted(filtered_params.items()))
        print(sorted_params)
        # 拼接参数字符串
        param_str = ''.join([f"{key}{value}" for key, value in sorted_params.items()])
        # 添加BaseKey并生成MD5
        sign_str = param_str + self.BK
        print(sign_str)
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    def process_excel(self, excel_path, base_url="http://112.25.126.97:8380"):
        """处理Excel文件并生成URL列表"""
        try:
            # 加载工作簿
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active

            # 获取表头映射（列索引到参数名）
            headers = {
                2: "channelId",  # 第三列
                3: "servicetype",  # 第四列
                4: "appid",  # 第五列
                5: "usertype",  # 第六列
                6: "userId",  # 第七列
                7: "msisdn",  # 第八列
                8: "bk"  # 第九列
            }

            # 清空现有URL列表
            self.generated_urls = []

            # 处理每一行数据（从第二行开始）
            for row in sheet.iter_rows(min_row=2, values_only=True):
                # 跳过空行
                if not any(row):
                    continue

                # 获取平台URL
                platform_url = row[1] if len(row) > 1 else None
                if not platform_url or not str(platform_url).startswith('http'):
                    continue

                # 解析平台URL路径
                parsed_url = urlparse(str(platform_url))
                path = parsed_url.path

                # 构建参数字典
                params = {}
                for col_idx, param_name in headers.items():
                    if len(row) > col_idx and row[col_idx] is not None:
                        params[param_name] = row[col_idx]

                # 添加固定参数
                params.update({
                    "seq": str(int(time.time() * 1000)),  # 时间戳
                })

                # 确保appid格式正确
                if "channelId" in params and "appid" not in params:
                    params["appid"] = f"{params['channelId']}000001"

                # 生成hash值（不包含hash参数本身）
                hash_params = params.copy()
                if 'hash' in hash_params:
                    del hash_params['hash']
                params['hash'] = self.generate_md5_hash(hash_params)

                # 构建查询字符串
                query = '&'.join([
                    f"{k}={quote(str(v))}"
                    for k, v in params.items()
                    if k != "bk"  # 排除BK参数
                ])

                # 构建完整URL
                url = urlunparse((
                    urlparse(base_url).scheme,
                    urlparse(base_url).netloc,
                    path,
                    '',
                    query,
                    ''
                ))

                # 保存渠道名称和生成的URL
                channel_name = row[0] if len(row) > 0 else "未知渠道"
                self.generated_urls.append({
                    "channel_name": channel_name,
                    "original_url": platform_url,
                    "generated_url": url,
                    "params": params
                })

            print(f"成功生成 {len(self.generated_urls)} 个URL")
            return True

        except Exception as e:
            print(f"处理Excel文件时出错: {e}")
            return False

    def save_to_file(self, output_path):
        """保存结果到文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for entry in self.generated_urls:
                    f.write(f"{entry['generated_url']}\n")
            print(f"结果已保存到 {output_path}")
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False

    def get_urls(self):
        """获取生成的URL列表"""
        return [entry['generated_url'] for entry in self.generated_urls]


# 使用示例
if __name__ == "__main__":
    # 配置参数
    EXCEL_PATH = "D:/Basekey2.xlsx"  # Excel文件路径
    OUTPUT_FILE = "../data/test_link.txt"  # 输出文件路径

    # 创建生成器实例
    generator = URLGenerator()

    # 处理Excel文件
    if generator.process_excel(EXCEL_PATH):
        # 保存结果
        generator.save_to_file(OUTPUT_FILE)

        # 打印前5个生成的URL
        print("\n示例生成的URL（前5个）:")
        for url in generator.get_urls()[:5]:
            print(url)

        # 打印第一个URL的详细参数
        if generator.generated_urls:
            print("\n第一个URL的详细参数:")
            print(json.dumps(generator.generated_urls[0]['params'], indent=2, ensure_ascii=False))