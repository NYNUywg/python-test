import json
import os
import time
from datetime import datetime

import requests
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from playwright.async_api import async_playwright
from pyppeteer import launch
import asyncio


def post(url, data):
    json_data = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'HWWAFSESID=090d6dcbb843b5c5e6; HWWAFSESTIME=1723626452297'
    }
    # 发送POST请求
    response = requests.post(url, headers=headers, data=json_data)
    return response


# 获取所有的公司uid
def get_all_uid():
    country_id = 7

    for i in range(1, 10):
        print("i", i)
        url = 'https://cloudapi.jctrans.com/era/fr/shop/companyDirectory'
        data = {
            "current": i,
            "size": 1000,
            "advCodeList": [],
            "vipCodeList": [],
            "minVipTotalYears": 0,
            "maxVipTotalYears": 150,
            "countryId": country_id
        }
        response = post(url, data)
        if response.status_code == 200:
            uid_list = []
            country_name = ""
            response_data = response.json()
            if 'data' in response_data:
                total = response_data['data']['total']
                if total == 0: # 结束
                    return
                data_records = response_data['data']['records']
                if data_records:
                    for record in data_records:
                        if 'uid' in record:
                            uid = record['uid']
                            uid_list.append(uid)
                        if 'countryName' in record and country_name == "":
                            country_name = record['countryName']
                print(
                    f"countryName:{country_name},country_id:{country_id},total:{total},len:{len(response_data['data']['records'])}")
                with open(f"./country/{country_name}_{country_id}_{total}.txt", 'a') as file:
                    for uid in uid_list:
                        file.write(uid + '\n')
                # return country_name, country_id, uid_list, total
            else:
                print('未找到 uid 字段')
        else:
            print('POST 请求失败')

    return None, None, None, None


def main():
    get_all_uid()
    return


if __name__ == '__main__':
    main()
