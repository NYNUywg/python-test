#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from datetime import datetime

def create_runner_script(script_name, country_name):
    """创建指定国家的运行脚本"""
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 爬虫 - {country_name}
自动生成于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from datetime import datetime

# 🍪 在这里设置你的Cookies
COOKIES_STRING = """visitor_type=old; visitor_type=old; PHPSESSID=v32jriqb7of4uj1kf5bbt8mbtp; Hm_lvt_ec1bbd5f641073ff6ffda17829b765b6=1749191542; Hm_lpvt_ec1bbd5f641073ff6ffda17829b765b6=1749191542; HMACCOUNT=C631C230EC9030F2; 53gid2=13516765440000; visitor_type=new; 53gid0=13516765440000; 53gid1=13516765440000; 53revisit=1749191542539; 53kf_72176590_from_host=glafamily.com; uuid_53kf_72176590=ef46e95e2c810f4541303981f96c0053; 53kf_72176590_land_page=https%253A%252F%252Fglafamily.com%252Flogin.php; kf_72176590_land_page_ok=1; 53uvid=1; onliner_zdfq72176590=0; _ga=GA1.1.1511340273.1749191543; password=glafamily123; remember=1; _ga_MVWVFBE4H9=GS2.1.s1749191543$o1$g0$t1749191559$j44$l0$h0; 53kf_72176590_keyword=https%3A%2F%2Fglafamily.com%2Fuserajax.php%3Faction%3Dlogin"""

# 🌍 目标国家
TARGET_COUNTRY = "{country_name}"

class CountryScraper:
    def __init__(self):
        print(f"🚀 启动 {{TARGET_COUNTRY}} 爬虫...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.set_cookies()
        
    def set_cookies(self):
        print("🍪 设置登录Cookies...")
        self.driver.get("https://glafamily.com")
        time.sleep(2)
        
        for cookie_pair in COOKIES_STRING.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                try:
                    self.driver.add_cookie({{
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.glafamily.com'
                    }})
                except:
                    pass
        
        self.driver.refresh()
        time.sleep(2)
        print("✅ Cookies设置完成")
    
    def extract_email(self, company_url, company_id):
        try:
            print(f"  -> 访问详情页: {{company_id}}")
            self.driver.get(company_url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            # 提取邮箱
            email_patterns = [
                r'Office email:\\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}})'
            ]
            
            for pattern in email_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    email = match.group(1)
                    print(f"  -> 📧 找到邮箱: {{email}}")
                    return email
            
            print(f"  -> ❌ 未找到邮箱")
            return ""
            
        except Exception as e:
            print(f"  -> ❌ 错误: {{e}}")
            return ""
    
    def extract_country_from_item(self, item):
        """从企业项目中提取国家信息"""
        # 提取国家信息
        country_elem = item.select_one('img[src*="/gj/"]')
        country = ""
        if country_elem:
            country_src = country_elem.get('src', '')
            if '/gj/' in country_src:
                country = country_src.split('/gj/')[1].split('.')[0].upper()
        return country
    
    def scrape_page(self, page_num=1):
        url = f"https://glafamily.com/member/public/index/directory/index.html?page={{page_num}}"
        print(f"\\n📄 抓取第 {{page_num}} 页 (目标国家: {{TARGET_COUNTRY}})...")
        
        self.driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        companies = []
        
        for item in soup.select('.list .item'):
            try:
                company_id = item.get('data-id', '')
                
                # 提取企业名称
                title_elem = item.select_one('.title')
                if title_elem:
                    for img in title_elem.find_all('img'):
                        img.decompose()
                    name = title_elem.get_text(strip=True)
                else:
                    continue
                
                # 提取国家信息
                country = self.extract_country_from_item(item)
                
                # 只处理目标国家的企业
                if TARGET_COUNTRY.upper() != country.upper():
                    continue
                
                # 提取邮箱
                detail_url = f"https://glafamily.com/member/public/index/company/index.html?id={{company_id}}"
                email = self.extract_email(detail_url, company_id) if company_id else ""
                
                companies.append({{
                    'country': country,
                    'company_name': name,
                    'email': email,
                    'company_id': company_id,
                    'detail_url': detail_url
                }})
                
                print(f"✅ {{name}} ({{country}}) - 📧 {{email if email else '无邮箱'}}")
                
            except Exception as e:
                print(f"❌ 错误: {{e}}")
                continue
        
        return companies
    
    def scrape_all_pages(self, max_pages=10):
        """抓取所有页面，只获取目标国家的企业"""
        all_companies = []
        
        for page in range(1, max_pages + 1):
            companies = self.scrape_page(page)
            all_companies.extend(companies)
            
            # 如果连续几页都没有目标国家的企业，可能已经抓完了
            if not companies:
                print(f"第 {{page}} 页没有找到 {{TARGET_COUNTRY}} 的企业")
                if page > 3:  # 连续3页没有数据就停止
                    break
            
            time.sleep(2)
        
        return all_companies
    
    def save_to_excel(self, companies):
        """保存数据到Excel文件"""
        if not companies:
            print("❌ 没有数据可保存")
            return
        
        # 创建DataFrame
        df = pd.DataFrame(companies)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{{TARGET_COUNTRY}}_companies_{{timestamp}}.xlsx"
        
        # 保存到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        emails_count = sum(1 for c in companies if c['email'])
        print(f"\\n💾 数据已保存到: {{filename}}")
        print(f"📊 {{TARGET_COUNTRY}} 企业: {{len(companies)}} 家")
        print(f"📧 获得邮箱: {{emails_count}} 个")
        
        return filename
    
    def close(self):
        self.driver.quit()

def main():
    print(f"🌍 GLA Family {{TARGET_COUNTRY}} 企业邮箱抓取器")
    print("=" * 50)
    
    # 询问抓取页数
    try:
        max_pages = int(input(f"请输入要抓取的页数 (建议10-20页): ") or "10")
    except:
        max_pages = 10
        print("使用默认值: 10页")
    
    scraper = CountryScraper()
    
    try:
        companies = scraper.scrape_all_pages(max_pages)
        
        if companies:
            filename = scraper.save_to_excel(companies)
            print(f"\\n🎉 {{TARGET_COUNTRY}} 数据抓取完成！")
        else:
            print(f"\\n😔 未找到 {{TARGET_COUNTRY}} 的企业数据")
        
    except KeyboardInterrupt:
        print("\\n⏹️ 用户中断抓取")
    except Exception as e:
        print(f"❌ 抓取过程中出错: {{e}}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
'''
    
    # 写入脚本文件
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_name, 0o755)
    print(f"✅ 已创建 {country_name} 爬虫脚本: {script_name}")

def main():
    print("🚀 GLA Family 多国家爬虫管理器")
    print("=" * 50)
    print("这个工具可以为不同国家创建独立的爬虫脚本")
    print("每个脚本会自动筛选指定国家的企业并提取邮箱")
    print()
    
    # 检查依赖
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("❌ 缺少必要的依赖包，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
        print("✅ 依赖包安装完成")
    
    while True:
        print("\n请选择操作:")
        print("1. 创建新的国家爬虫脚本")
        print("2. 查看已创建的脚本")
        print("3. 运行指定脚本")
        print("4. 退出")
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "1":
            # 创建新脚本
            country_name = input("请输入国家名称 (如: China, USA, Germany): ").strip()
            if not country_name:
                print("❌ 国家名称不能为空")
                continue
            
            script_num = input("请输入脚本编号 (如: 1, 2, 3): ").strip() or "1"
            script_name = f"run{script_num}.py"
            
            if os.path.exists(script_name):
                overwrite = input(f"⚠️ {script_name} 已存在，是否覆盖? (y/n): ").strip().lower()
                if overwrite != 'y':
                    continue
            
            create_runner_script(script_name, country_name)
            
        elif choice == "2":
            # 查看已创建的脚本
            scripts = [f for f in os.listdir('.') if f.startswith('run') and f.endswith('.py')]
            if scripts:
                print("\n📋 已创建的脚本:")
                for script in sorted(scripts):
                    print(f"  - {script}")
            else:
                print("\n📋 还没有创建任何脚本")
        
        elif choice == "3":
            # 运行指定脚本
            scripts = [f for f in os.listdir('.') if f.startswith('run') and f.endswith('.py')]
            if not scripts:
                print("❌ 没有可运行的脚本")
                continue
            
            print("\n📋 可运行的脚本:")
            for i, script in enumerate(sorted(scripts), 1):
                print(f"  {i}. {script}")
            
            try:
                script_choice = int(input("请选择要运行的脚本编号: ")) - 1
                if 0 <= script_choice < len(scripts):
                    script_name = sorted(scripts)[script_choice]
                    print(f"🚀 启动 {script_name}...")
                    subprocess.run([sys.executable, script_name])
                else:
                    print("❌ 无效的脚本编号")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == "4":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main() 