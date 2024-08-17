import json
import time

import requests
from lxml import etree
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.util import wait
from lxml import html
from playwright.sync_api import sync_playwright


def user_login(driver):
    # 读取用户名和密码
    with open('user.txt', 'r') as file:
        lines = file.readlines()
        username = lines[0].split(': ')[1].strip()
        password = lines[1].split(': ')[1].strip()

    # 打开登录网页
    login_url = 'https://passport.jctrans.com/login'
    driver.get(login_url)

    switch_input = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/img')
    switch_input.click()

    # 定位用户名输入框并输入用户名
    username_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[1]/div[2]/div[1]/form/div[1]/div/div/div/div/div/input')
    username_input.send_keys(username)

    # 定位密码输入框并输入密码
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[1]/div[2]/div[1]/form/div[2]/div/div/div/div/div/input')
    password_input.send_keys(password)

    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[3]/div[3]/div[3]/button')
    login_button.click()

    time.sleep(10)

    cookies = driver.get_cookies()
    # 添加异常处理，捕获可能出现的异常
    try:
        # 执行其他操作
        pass
    except NoSuchElementException as e:
        print("Element not found: ", e)
    driver.close()
    return cookies


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
    # driver = webdriver.Chrome()
    # home_url = 'https://jctrans.com/cn/membership/list?countryId=suJGxhhfuX5knrcfkHDRZg%3D%3D&redirectFrom=ERA' # 斯里兰卡
    # driver.get(home_url)
    url = 'https://cloudapi.jctrans.com/era/fr/shop/companyDirectory'
    data = {
        "current": 1,
        "size": 20,
        "advCodeList": [],
        "vipCodeList": [],
        "minVipTotalYears": 0,
        "maxVipTotalYears": 150,
        "countryId": 67
    }
    print('countryId：', 67)
    response = post(url, data)
    if response.status_code == 200:
        uid_list = []
        response_data = response.json()
        if 'data' in response_data:
            print('uId总数：', response_data['data']['total'])
            data_records = response_data['data']['records']
            if data_records:
                for record in data_records:
                    if 'uid' in record:
                        uid = record['uid']
                        uid_list.append(uid)
            return uid_list
        else:
            print('未找到 uid 字段')
    else:
        print('POST 请求失败')


def get_index_context(url, cookies):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 设置附带 cookie 的请求头
        headers = {
            'Cookie': '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        }
        page.set_extra_http_headers(headers)

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
    uid_list = get_all_uid()
    for uid in uid_list:
        # https://www.jctrans.com/cn/home/963d2723459700775661af809ad2a1d9
        url = 'https://www.jctrans.com/cn/home/' + uid
        # print(url)
        company, email = get_index_context(url)
        print(company, email)


if __name__ == '__main__':
    # main()
    driver = webdriver.Chrome()
    cookies = user_login(driver)
    print(cookies)
    company, email = get_index_context('https://www.jctrans.com/cn/home/963d2723459700775661af809ad2a1d9', cookies)
    print(company, email)

