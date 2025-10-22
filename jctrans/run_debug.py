import json
import os
import re

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
    
    print(f"Navigating to {url}...")
    await page.goto(url)
    await page.wait_for_load_state('networkidle')
    
    # Save screenshot for debugging
    screenshot_path = 'debug_screenshot.png'
    await page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Save page HTML for debugging
    html_content = await page.content()
    html_path = 'debug_page.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Page HTML saved to {html_path}")
    
    # Try to find company name - look for h1 or title elements
    try:
        # Try h1 tag first (common for company names)
        h1_elements = await page.locator('h1').all()
        print(f"Found {len(h1_elements)} h1 elements")
        for i, h1 in enumerate(h1_elements):
            text = await h1.inner_text()
            print(f"  h1[{i}]: {text[:100]}")
        
        if h1_elements:
            company = await h1_elements[0].inner_text()
            company = company.strip()
    except Exception as e:
        print(f"Error finding h1: {e}")
    
    # Try alternative selectors for company name
    if not company:
        try:
            # Try .title class
            title_elements = await page.locator('.title').all()
            print(f"Found {len(title_elements)} .title elements")
            if title_elements:
                company = await title_elements[0].inner_text()
                company = company.strip()
                print(f"Found company from .title: {company}")
        except Exception as e:
            print(f"Error finding .title: {e}")
    
    # If still no company, try the section header
    if not company:
        try:
            # Look for company name in page structure
            company_selectors = [
                'css=section h2',
                'css=.company-name',
                'css=[class*="company"]',
            ]
            for selector in company_selectors:
                elements = await page.locator(selector).all()
                if elements:
                    company = await elements[0].inner_text()
                    company = company.strip()
                    print(f"Found company from {selector}: {company}")
                    break
        except Exception as e:
            print(f"Error in alternative search: {e}")

    # Try to find contact information
    try:
        content_elements = await page.locator('.content').all()
        print(f"Total .content elements: {len(content_elements)}")
        
        # Print all .content elements for debugging
        for i, elem in enumerate(content_elements):
            text = await elem.inner_text()
            print(f"  .content[{i}]: {text[:50]}...")
        
        # Extract email and phone by searching through all content elements
        for elem in content_elements:
            text = await elem.inner_text()
            text = text.strip()
            
            # Find email (contains @)
            if "@" in text and not email:
                email = text
                print(f"Found email: {email}")
            
            # Find phone (starts with + or is all digits, and length between 7-15)
            # Skip if it contains @ (to avoid email addresses)
            if not phone and "@" not in text:
                # Check if it looks like a phone number
                clean_text = text.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if clean_text.isdigit() and 7 <= len(clean_text) <= 15:
                    # Prefer the one with + prefix if available
                    if not phone or (text.startswith("+") and not phone.startswith("+")):
                        phone = text
                        print(f"Found phone: {phone}")
        
    except Exception as e:
        print(f"Error getting contact info: {e}")
    
    print(f"\n=== Extracted Data ===")
    print(f"Company: {company}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"======================\n")
    
    return company, email, phone


async def fetch_data_with_retry(page, url, retry=3):  # Reduced retry for debugging
    for attempt in range(retry):
        try:
            print(f"\nAttempt {attempt + 1}/{retry}")
            company, email, phone = await get_index_context(page, url)
            return company, email, phone
        except Exception as e:
            print(f"Failed to fetch data from {url}. Retrying...")
            print(f"Error: {e}")
    return None, None, None


async def main(country_id, country_name, total):
    cookie_value = "b7f5a216bf394d1cac4d2a394da0617a"
    country_name, country_id, uid_list, total, count = get_all_uid(country_id,country_name,total)
    
    # Only process first UID for debugging
    uid_list = uid_list[:1]
    print(f"Processing {len(uid_list)} URL(s) for debugging...")

    async with async_playwright() as p:
        # Launch browser in non-headless mode for debugging
        browser = await p.chromium.launch(headless=False, slow_mo=1000)  # slow_mo helps see what's happening
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = await context.new_page()
        
        await context.add_cookies([{
            "domain": ".jctrans.com",
            "name": "JC-JAVA-Token-Root",
            "path": "/",
            "value": cookie_value
        }])

        for uid in uid_list:
            url = 'https://www.jctrans.com/cn/store/home/' + uid
            company, email, phone = await fetch_data_with_retry(page, url)
            count += 1
            print(f"\nResult {count}: Company={company}, Email={email}, Phone={phone}")
            
            if company or email or phone:
                filename = f"{country_name}_{country_id}_{total}.xlsx"
                append_to_excel([company, email, phone], filename)
        
        print("\nDebug session complete. Press Enter to close browser...")
        input()
        await browser.close()


def clean_excel_string(s):
    if isinstance(s, str):
        # 去除所有非法字符
        return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)
    return s

