import json
import os
import time
from datetime import datetime

import requests
from openpyxl.workbook import Workbook
from playwright.sync_api import sync_playwright


def create_excel(data, filename):
    # 创建一个新的 Excel 工作簿
    wb = Workbook()
    ws = wb.active
    # 将数据写入工作表
    for row in data:
        ws.append(row)
    # 保存 Excel 文件
    directory = 'data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, filename)
    wb.save(filename)
    print("创建成功：", filename)


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
def get_all_uid(country_id):
    url = 'https://cloudapi.jctrans.com/era/fr/shop/companyDirectory'
    data = {
        "current": 1,
        "size": 100000,
        "advCodeList": [],
        "vipCodeList": [],
        "minVipTotalYears": 0,
        "maxVipTotalYears": 150,
        "countryId": country_id
    }
    response = post(url, data)
    if response.status_code == 200:
        uid_list = []
        response_data = response.json()
        if 'data' in response_data:
            total = response_data['data']['total']
            data_records = response_data['data']['records']
            if data_records:
                for record in data_records:
                    if 'uid' in record:
                        uid = record['uid']
                        uid_list.append(uid)
            print(f"country_id:{country_id},total:{total}")
            return uid_list, total
        else:
            print('未找到 uid 字段')
    else:
        print('POST 请求失败')


def get_index_context(url, cookie_value):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        context.add_cookies([{
            "domain": ".jctrans.com",
            "name": "JC-JAVA-Token",
            "path": "/",
            "value": cookie_value
        }])

        page.goto(url)

        page.wait_for_load_state('networkidle')

        # 获取公司名称
        h1_elements = page.locator('xpath=//h1').all()
        company = h1_elements[2].inner_text()

        # 获取邮箱
        content_elements = page.locator('.content').all()
        email = content_elements[-2].inner_text()

        browser.close()
        return company, email


def main():
    cookie_value = "d729c67db0b2489d9ad4080670528b0b"
    country_id = 67
    uid_list, total = get_all_uid(country_id)
    index_data_list = [[]]
    for uid in uid_list:
        # https://www.jctrans.com/cn/home/963d2723459700775661af809ad2a1d9
        url = 'https://www.jctrans.com/cn/home/' + uid
        # print(url)
        company, email = get_index_context(url, cookie_value)
        index_data_list.append([company, email])
        print(company, email)
    # 创建xlsx
    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"斯里兰卡_{country_id}_{total}_{current_time}.xlsx"
    create_excel(index_data_list, filename)


if __name__ == '__main__':
    main()
