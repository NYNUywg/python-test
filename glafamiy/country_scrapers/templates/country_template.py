#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 国家爬虫模板
使用方法：
1. 修改下面的 TARGET_COUNTRY 为你要抓取的国家名
2. 直接运行脚本
3. 支持断点续传，会自动从上次停止的地方继续
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from datetime import datetime
import os

# 🌍 在这里设置目标国家名称 (修改这里即可)
TARGET_COUNTRY = "Saudi Arabia"  # 例如: "China", "United States", "Germany", "Saudi Arabia", "United Arab Emirates"

# 🍪 登录Cookies (所有脚本共用)
COOKIES_STRING = """visitor_type=old; visitor_type=old; PHPSESSID=v32jriqb7of4uj1kf5bbt8mbtp; Hm_lvt_ec1bbd5f641073ff6ffda17829b765b6=1749191542; HMACCOUNT=C631C230EC9030F2; 53gid2=13516765440000; 53gid0=13516765440000; 53gid1=13516765440000; 53revisit=1749191542539; 53kf_72176590_from_host=glafamily.com; uuid_53kf_72176590=ef46e95e2c810f4541303981f96c0053; 53kf_72176590_land_page=https%253A%252F%252Fglafamily.com%252Flogin.php; kf_72176590_land_page_ok=1; 53uvid=1; onliner_zdfq72176590=0; _ga=GA1.1.1511340273.1749191543; 53kf_72176590_keyword=https%3A%2F%2Fglafamily.com%2Fuserajax.php%3Faction%3Dlogin; Hm_lpvt_ec1bbd5f641073ff6ffda17829b765b6=1749215109; visitor_type=old; _ga_MVWVFBE4H9=GS2.1.s1749215110$o2$g0$t1749215115$j55$l0$h0; password=glafamily123; remember=1"""

class CountryScraper:
    def __init__(self):
        self.target_country = TARGET_COUNTRY.upper()
        
        # 确保data目录存在
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        self.excel_filename = os.path.join(data_dir, f"{self.target_country.replace(' ', '_')}_companies.xlsx")
        
        print(f"🚀 启动 {TARGET_COUNTRY} 爬虫...")
        print(f"📄 Excel文件: {self.excel_filename}")
        
        # 检查现有数据，确定起始位置
        self.start_page, self.start_company = self.get_resume_position()
        
        # 初始化浏览器
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.set_cookies()
        
    def get_resume_position(self):
        """检查现有Excel文件，确定从哪里开始抓取"""
        if not os.path.exists(self.excel_filename):
            print("📝 创建新的Excel文件")
            return 1, 0
        
        try:
            df = pd.read_excel(self.excel_filename, engine='openpyxl')
            existing_count = len(df)
            
            if existing_count == 0:
                print("📝 Excel文件为空，从第1页开始")
                return 1, 0
            
            # 假设每页大约13家企业，计算应该从哪一页开始
            estimated_page = (existing_count // 13) + 1
            companies_in_current_page = existing_count % 13
            
            print(f"📊 发现已有数据: {existing_count} 家企业")
            print(f"🔄 预计从第 {estimated_page} 页第 {companies_in_current_page + 1} 家企业开始")
            
            return estimated_page, companies_in_current_page
            
        except Exception as e:
            print(f"⚠️ 读取Excel文件出错: {e}")
            print("📝 重新开始抓取")
            return 1, 0
    
    def set_cookies(self):
        """设置登录Cookies"""
        print("🍪 设置登录Cookies...")
        self.driver.get("https://glafamily.com")
        time.sleep(2)
        
        for cookie_pair in COOKIES_STRING.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                try:
                    self.driver.add_cookie({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.glafamily.com'
                    })
                except:
                    pass
        
        self.driver.refresh()
        time.sleep(2)
        print("✅ Cookies设置完成")
    
    def extract_email(self, company_url, company_id):
        """提取企业邮箱"""
        try:
            print(f"  -> 访问详情页: {company_id}")
            self.driver.get(company_url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            # 提取邮箱
            email_patterns = [
                r'Office email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            for pattern in email_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    email = match.group(1)
                    print(f"  -> 📧 找到邮箱: {email}")
                    return email
            
            print(f"  -> ❌ 未找到邮箱")
            return ""
            
        except Exception as e:
            print(f"  -> ❌ 错误: {e}")
            return ""
    
    def extract_country_from_item(self, item):
        """从企业项目中提取国家信息"""
        country_elem = item.select_one('img[src*="/gj/"]')
        country = ""
        if country_elem:
            country_src = country_elem.get('src', '')
            if '/gj/' in country_src:
                country = country_src.split('/gj/')[1].split('.')[0].upper()
        return country
    
    def scrape_page(self, page_num=1, skip_companies=0):
        """抓取指定页面"""
        url = f"https://glafamily.com/member/public/index/directory/index.html?page={page_num}"
        print(f"\n📄 抓取第 {page_num} 页 (目标国家: {TARGET_COUNTRY})...")
        
        self.driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        companies = []
        processed_count = 0
        
        for item in soup.select('.list .item'):
            try:
                # 如果需要跳过前面的企业（断点续传）
                if processed_count < skip_companies:
                    processed_count += 1
                    continue
                
                company_id = item.get('data-id', '')
                
                # 提取企业名称
                title_elem = item.select_one('.title')
                if title_elem:
                    for img in title_elem.find_all('img'):
                        img.decompose()
                    name = title_elem.get_text(strip=True)
                else:
                    processed_count += 1
                    continue
                
                # 提取国家信息
                country = self.extract_country_from_item(item)
                
                # 只处理目标国家的企业
                if self.target_country != country.upper():
                    processed_count += 1
                    continue
                
                # 提取邮箱
                detail_url = f"https://glafamily.com/member/public/index/company/index.html?id={company_id}"
                email = self.extract_email(detail_url, company_id) if company_id else ""
                
                company_data = {
                    'country': country,
                    'company_name': name,
                    'email': email,
                    'company_id': company_id,
                    'detail_url': detail_url,
                    'scraped_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                companies.append(company_data)
                print(f"✅ {name} ({country}) - 📧 {email if email else '无邮箱'}")
                
                # 立即保存到Excel（追加模式）
                self.append_to_excel([company_data])
                
                processed_count += 1
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                processed_count += 1
                continue
        
        return companies
    
    def append_to_excel(self, companies):
        """追加数据到Excel文件"""
        if not companies:
            return
        
        df_new = pd.DataFrame(companies)
        
        if os.path.exists(self.excel_filename):
            # 文件存在，追加数据
            df_existing = pd.read_excel(self.excel_filename, engine='openpyxl')
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            # 文件不存在，创建新文件
            df_combined = df_new
        
        # 保存到Excel
        df_combined.to_excel(self.excel_filename, index=False, engine='openpyxl')
        
        total_count = len(df_combined)
        emails_count = sum(1 for _, row in df_combined.iterrows() if row['email'])
        
        print(f"💾 已保存到 {self.excel_filename} (总计: {total_count} 家企业, 邮箱: {emails_count} 个)")
    
    def scrape_all_pages(self, max_pages=50):
        """抓取所有页面"""
        print(f"🎯 开始抓取 {TARGET_COUNTRY} 企业数据")
        print(f"📊 最大页数: {max_pages}")
        print(f"🔄 从第 {self.start_page} 页开始")
        
        total_found = 0
        consecutive_empty_pages = 0
        
        for page in range(self.start_page, max_pages + 1):
            try:
                # 第一页可能需要跳过一些企业
                skip_companies = self.start_company if page == self.start_page else 0
                
                companies = self.scrape_page(page, skip_companies)
                
                if companies:
                    total_found += len(companies)
                    consecutive_empty_pages = 0
                    print(f"📈 第 {page} 页找到 {len(companies)} 家 {TARGET_COUNTRY} 企业")
                else:
                    consecutive_empty_pages += 1
                    print(f"📭 第 {page} 页没有找到 {TARGET_COUNTRY} 企业")
                
                # 如果连续5页都没有目标国家的企业，可能已经抓完了
                if consecutive_empty_pages >= 5:
                    print(f"🏁 连续 {consecutive_empty_pages} 页没有找到 {TARGET_COUNTRY} 企业，停止抓取")
                    break
                
                # 重置起始位置（只在第一页有效）
                self.start_company = 0
                
                time.sleep(2)  # 避免请求过快
                
            except KeyboardInterrupt:
                print(f"\n⏹️ 用户中断，已保存到第 {page} 页")
                break
            except Exception as e:
                print(f"❌ 第 {page} 页抓取出错: {e}")
                continue
        
        print(f"\n🎉 抓取完成！总共找到 {total_found} 家 {TARGET_COUNTRY} 企业")
        return total_found
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()

def main():
    print(f"🌍 GLA Family {TARGET_COUNTRY} 企业邮箱抓取器")
    print("=" * 60)
    print(f"🎯 目标国家: {TARGET_COUNTRY}")
    print("✨ 支持断点续传，自动追加到Excel文件")
    print("📊 将抓取所有可用页面")
    print()
    
    scraper = CountryScraper()
    
    try:
        # 直接使用默认最大页数，不需要用户输入
        max_pages = 250  # 设置一个足够大的数值来抓取所有页面
        
        # 开始抓取
        total_found = scraper.scrape_all_pages(max_pages)
        
        if total_found > 0:
            print(f"\n📊 最终统计:")
            print(f"   - Excel文件: {scraper.excel_filename}")
            print(f"   - 企业数量: {total_found} 家")
            print(f"   - 目标国家: {TARGET_COUNTRY}")
        else:
            print(f"\n😔 未找到 {TARGET_COUNTRY} 的企业数据")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断抓取")
    except Exception as e:
        print(f"❌ 抓取过程中出错: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 