import json
import os
import re
import asyncio
import random

import requests
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from playwright.async_api import async_playwright


def append_to_excel(data, filename):
    directory = 'data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, filename)
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
    # 过滤每个字段
    clean_data = [clean_excel_string(x) for x in data]
    ws.append(clean_data)
    wb.save(filename)


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
def get_all_uid(country_id,country_name,total):
    uid_list = []

    # 读取文件
    workbook_path = f"./data/{country_name}_{country_id}_{total}.xlsx"
    if os.path.exists(workbook_path):
        workbook = load_workbook(workbook_path)
        sheet = workbook.active
        start_line_number = sheet.max_row + 1
    else:
        start_line_number = 1
    with open(f"./country/{country_name}_{country_id}_{total}.txt", 'r') as file:
        lines = file.readlines()
        for line_number, line in enumerate(lines, start=1):
            if line_number < start_line_number:
                continue
            uid_list.append(line.strip())
    return country_name, country_id, uid_list, total, start_line_number


async def get_index_context(page, url):
    company = ""
    email = ""
    phone = ""
    
    # 增加超时时间并使用 domcontentloaded 而不是 load
    await page.goto(url, timeout=60000, wait_until='domcontentloaded')
    await page.wait_for_load_state('networkidle', timeout=60000)
    
    # Find company name - try h1 tag first
    try:
        h1_elements = await page.locator('h1').all()
        if h1_elements:
            company = await h1_elements[0].inner_text()
            company = company.strip()
    except Exception:
        pass
    
    # Try alternative selectors for company name if not found
    if not company:
        try:
            title_elements = await page.locator('.title').all()
            if title_elements:
                company = await title_elements[0].inner_text()
                company = company.strip()
        except Exception:
            pass
    
    # Extract email and phone from .content elements
    try:
        content_elements = await page.locator('.content').all()
        
        # Search through all content elements to find email and phone
        for elem in content_elements:
            text = await elem.inner_text()
            text = text.strip()
            
            # Find email (contains @)
            if "@" in text and not email:
                email = text
            
            # Find phone (looks like a phone number)
            if not phone and "@" not in text:
                clean_text = text.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if clean_text.isdigit() and 7 <= len(clean_text) <= 15:
                    # Prefer the one with + prefix if available
                    if not phone or (text.startswith("+") and not phone.startswith("+")):
                        phone = text
    except Exception:
        pass
    
    return company, email, phone


async def fetch_data_with_retry(page, url, retry=3):
    for attempt in range(retry):
        try:
            company, email, phone = await get_index_context(page, url)
            return company, email, phone
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retry} failed for {url}: {str(e)[:100]}")
            if attempt < retry - 1:
                # 等待一段时间后重试，使用指数退避
                wait_time = (attempt + 1) * 5
                print(f"Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            else:
                print(f"Failed to fetch data from {url} after {retry} attempts")
    return None, None, None


async def main(country_id, country_name, total):
    cookie_value = "b285788fb6414b31b22edea249087d42"

    country_name, country_id, uid_list, total, count = get_all_uid(country_id, country_name, total)

    async with async_playwright() as p:
        # 添加更多浏览器选项来模拟真实用户
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        # 添加额外的 JavaScript 来隐藏自动化特征
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        # 设置默认超时
        page.set_default_timeout(60000)
        
        await context.add_cookies([{
            "domain": ".jctrans.com",
            "name": "JC-JAVA-Token-Root",
            "path": "/",
            "value": cookie_value
        }])

        for uid in uid_list:
            url = 'https://www.jctrans.com/cn/store/home/' + uid
            
            # 添加随机延迟，模拟人类行为（2-5秒）
            delay = random.uniform(0, 0.2)
            print(f"Waiting {delay:.1f}s before next request...")
            await asyncio.sleep(delay)
            
            company, email, phone = await fetch_data_with_retry(page, url)
            count += 1
            print(f"{count}: {company} | {email} | {phone}")
            
            # 只有成功获取数据才保存
            if company or email or phone:
                filename = f"{country_name}_{country_id}_{total}.xlsx"
                append_to_excel([company, email, phone], filename)
            else:
                print(f"Warning: No data extracted for {url}")
                
        await browser.close()


def clean_excel_string(s):
    if isinstance(s, str):
        # 去除所有非法字符
        return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)
    return s



