from selenium import webdriver
from selenium.webdriver.common.by import By

# https://www.jctrans.com/

# def user_login(driver):
#     # 读取用户名和密码
#     with open('user.txt', 'r') as file:
#         lines = file.readlines()
#         username = lines[0].split(': ')[1].strip()
#         password = lines[1].split(': ')[1].strip()
#
#     # 打开登录网页
#     login_url = 'https://passport.jctrans.com/login'
#     driver.get(login_url)
#
#     switch_input = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/img')
#     switch_input.click()
#
#     # 定位用户名输入框并输入用户名
#     username_input = driver.find_element(By.XPATH,
#                                          '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[1]/div[2]/div[1]/form/div[1]/div/div/div/div/div/input')
#     username_input.send_keys(username)
#
#     # 定位密码输入框并输入密码
#     password_input = driver.find_element(By.XPATH,
#                                          '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[1]/div[2]/div[1]/form/div[2]/div/div/div/div/div/input')
#     password_input.send_keys(password)
#
#     # 点击登录按钮
#     login_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[3]/button')
#     login_button.click()
#
#     time.sleep(10)
#
#     cookies = driver.get_cookies()
#     # 添加异常处理，捕获可能出现的异常
#     try:
#         # 执行其他操作
#         pass
#     except NoSuchElementException as e:
#         print("Element not found: ", e)
#     driver.close()
#     return cookies

import json
import os
import time
from datetime import datetime

import requests
from openpyxl.workbook import Workbook
from playwright.async_api import async_playwright


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


async def get_index_context(page, url):
    company = ""
    email = ""
    phone = ""
    await page.goto(url)
    await page.wait_for_load_state('networkidle')

    h1_elements = await page.locator('xpath=//h1').all()
    if len(h1_elements) >= 2:
        company = await h1_elements[2].inner_text()

    content_elements = await page.locator('.content').all()
    if len(content_elements) >= 3:
        email = await content_elements[-3].inner_text()
    if len(content_elements) >= 2:
        phone = await content_elements[-2].inner_text()
    if "@" in email:
        pass
    else:
        email = phone
        phone = ""
    return company, email, phone


async def main():
    cookie_value = "d729c67db0b2489d9ad4080670528b0b"
    country_id = 92
    uid_list, total = get_all_uid(country_id)
    index_data_list = [[]]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await context.add_cookies([{
            "domain": ".jctrans.com",
            "name": "JC-JAVA-Token",
            "path": "/",
            "value": cookie_value
        }])

        count = 0
        for uid in uid_list:
            url = 'https://www.jctrans.com/cn/home/' + uid
            company, email, phone = await get_index_context(page, url)
            count += 1
            print(count, company, email, phone)
            index_data_list.append([company, email, phone])
        await browser.close()

    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"巴基斯坦_{country_id}_{total}_{current_time}.xlsx"
    create_excel(index_data_list, filename)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
