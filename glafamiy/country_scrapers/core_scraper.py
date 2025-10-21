#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLA Family 核心爬虫类
所有国家爬虫的通用功能
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from datetime import datetime
import os

# 🔐 登录凭据
LOGIN_EMAIL = "aria.zhang@hippoinfinite.com"
LOGIN_PASSWORD = "glafamily123"

class CountryScraper:
    def __init__(self, target_country):
        self.target_country = target_country
        
        # 确保data目录存在
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        self.excel_filename = os.path.join(data_dir, f"{self.target_country.replace(' ', '_').upper()}_companies.xlsx")
        
        print(f"🚀 启动 {target_country} 爬虫...")
        print(f"📄 Excel文件: {self.excel_filename}")
        
        # 检查现有数据，确定起始位置
        self.start_page, self.start_company = self.get_resume_position()
        
        # 初始化浏览器
        options = webdriver.ChromeOptions()
        
        # 后台运行选项 - 不抢夺屏幕控制权
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')  # 禁用GPU加速
        options.add_argument('--disable-web-security')  # 禁用web安全
        options.add_argument('--disable-features=VizDisplayCompositor')  # 禁用显示合成器
        options.add_argument('--window-size=1920,1080')  # 设置窗口大小
        options.add_argument('--disable-extensions')  # 禁用扩展
        options.add_argument('--disable-plugins')  # 禁用插件
        options.add_argument('--disable-images')  # 禁用图片加载（提高速度）
        
        # 设置用户代理
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        print("🔧 启动后台浏览器（无界面模式）...")
        
        # 尝试使用系统Chrome驱动，如果失败则尝试自动下载
        try:
            # 首先尝试使用系统路径的chromedriver
            self.driver = webdriver.Chrome(options=options)
        except:
            try:
                # 如果系统路径失败，尝试自动下载
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except:
                print("❌ 无法启动Chrome浏览器，请确保已安装Chrome和chromedriver")
                raise Exception("Chrome驱动初始化失败")
        
        # 设置登录并验证登录
        if not self.login():
            print("❌ 登录失败，无法继续")
            self.driver.quit()
            raise Exception("登录失败")
        
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
    
    def login(self):
        """登录并验证登录状态"""
        print("🔐 尝试登录...")
        
        # 访问登录页面
        self.driver.get("https://glafamily.com/login.php")
        time.sleep(5)
        
        try:
            # 等待页面加载完成
            wait = WebDriverWait(self.driver, 20)
            
            print("🔍 查找登录表单字段...")
            
            # 先调试：查看页面上所有的input元素
            print("🔍 调试：分析页面上的所有输入字段...")
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"📋 找到 {len(all_inputs)} 个输入字段:")
            
            for i, input_elem in enumerate(all_inputs):
                try:
                    input_type = input_elem.get_attribute("type") or "text"
                    input_name = input_elem.get_attribute("name") or ""
                    input_placeholder = input_elem.get_attribute("placeholder") or ""
                    input_id = input_elem.get_attribute("id") or ""
                    input_value = input_elem.get_attribute("value") or ""
                    is_displayed = input_elem.is_displayed()
                    print(f"  {i+1}. type='{input_type}', name='{input_name}', placeholder='{input_placeholder}', id='{input_id}', value='{input_value}', visible={is_displayed}")
                except:
                    print(f"  {i+1}. [无法读取属性]")
            
            # 等待并查找User Email字段
            username_field = None
            
            # 尝试多种方式查找邮箱字段
            email_selectors = [
                (By.NAME, "userName"),  # 根据调试信息，这是可见的用户名字段
                (By.NAME, "email"),
                (By.ID, "user_email"),
                (By.CSS_SELECTOR, "input[placeholder*='E-mail']"),
                (By.CSS_SELECTOR, "input[type='text'][name='email']"),
                (By.XPATH, "//input[@name='email']"),
                (By.XPATH, "//input[@id='user_email']")
            ]
            
            for selector_type, selector_value in email_selectors:
                try:
                    print(f"🔍 尝试查找邮箱字段: {selector_type} = {selector_value}")
                    elements = self.driver.find_elements(selector_type, selector_value)
                    if elements:
                        for elem in elements:
                            if elem.is_displayed():
                                username_field = elem
                                print(f"✅ 找到可见的邮箱字段: {selector_value}")
                                break
                        if username_field:
                            break
                except Exception as e:
                    print(f"  ❌ 查找失败: {e}")
                    continue
            
            if not username_field:
                print("❌ 未找到User Email字段")
                return False
            
            # 等待并查找Password字段
            password_field = None
            
            password_selectors = [
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@name='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    print(f"🔍 尝试查找密码字段: {selector_type} = {selector_value}")
                    elements = self.driver.find_elements(selector_type, selector_value)
                    if elements:
                        for elem in elements:
                            if elem.is_displayed():
                                password_field = elem
                                print(f"✅ 找到可见的密码字段: {selector_value}")
                                break
                        if password_field:
                            break
                except Exception as e:
                    print(f"  ❌ 查找失败: {e}")
                    continue
            
            if not password_field:
                print("❌ 未找到Password字段")
                return False
            
            # 滚动到登录表单区域并等待
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", username_field)
            time.sleep(3)
            
            # 使用JavaScript直接设置值（避免交互问题）
            print("📝 输入邮箱地址...")
            self.driver.execute_script("arguments[0].value = '';", username_field)
            self.driver.execute_script("arguments[0].value = arguments[1];", username_field, LOGIN_EMAIL)
            time.sleep(1)
            
            print("📝 输入密码...")
            self.driver.execute_script("arguments[0].value = '';", password_field)
            self.driver.execute_script("arguments[0].value = arguments[1];", password_field, LOGIN_PASSWORD)
            time.sleep(1)
            
            # 触发change事件确保表单识别输入
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", username_field)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", password_field)
            time.sleep(1)
            
            # 查找Login按钮
            print("🔍 查找Login按钮...")
            login_button = None
            
            # 尝试多种方式查找Login按钮
            try:
                # 首先尝试通过value属性查找
                login_button = self.driver.find_element(By.CSS_SELECTOR, "input[value='Login']")
                print("✅ 找到Login按钮 (通过value)")
            except:
                try:
                    # 尝试查找所有submit按钮
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                    for btn in submit_buttons:
                        btn_value = btn.get_attribute("value") or ""
                        if "login" in btn_value.lower():
                            login_button = btn
                            print(f"✅ 找到Login按钮: {btn_value}")
                            break
                except:
                    pass
            
            # 点击登录按钮
            if login_button:
                try:
                    # 滚动到按钮位置
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", login_button)
                    time.sleep(2)
                    
                    # 使用JavaScript点击（更可靠）
                    self.driver.execute_script("arguments[0].click();", login_button)
                    print("✅ 点击Login按钮")
                except:
                    # 如果JavaScript点击失败，尝试普通点击
                    login_button.click()
                    print("✅ 点击Login按钮 (fallback)")
            else:
                # 如果找不到按钮，尝试提交表单
                print("⚠️ 未找到Login按钮，尝试提交表单...")
                self.driver.execute_script("arguments[0].form.submit();", password_field)
            
            # 等待页面跳转
            print("⏳ 等待登录结果...")
            time.sleep(8)
            
            # 验证登录结果
            current_url = self.driver.current_url
            print(f"📍 登录后URL: {current_url}")
            
            # 检查是否成功登录
            if 'login' not in current_url.lower():
                print("✅ 登录成功")
                return True
            else:
                print("❌ 登录失败，仍在登录页面")
                
                # 检查页面内容是否有错误信息
                try:
                    page_source = self.driver.page_source.lower()
                    if any(keyword in page_source for keyword in ["incorrect", "invalid", "error", "wrong", "failed"]):
                        print("⚠️ 可能的错误：用户名或密码不正确")
                    else:
                        print("⚠️ 登录失败，原因未知")
                except:
                    pass
                
                return False
                
        except Exception as e:
            print(f"❌ 登录过程出错: {e}")
            return False
    
    def search_by_country(self):
        """访问目录页面并按国家搜索"""
        print(f"🔍 搜索 {self.target_country} 企业...")
        
        # 访问目录页面
        self.driver.get("https://glafamily.com/member/public/index/directory/")
        time.sleep(5)
        
        try:
            # 等待页面加载完成
            wait = WebDriverWait(self.driver, 15)
            
            # 查找layui国家选择框
            print("🔍 查找layui国家选择框...")
            
            # 点击国家选择框来展开选项
            country_selector = None
            selectors = [
                "//div[@class='layui-select-title' and .//input[@placeholder='Please Select Country']]",
                "//input[@placeholder='Please Select Country']/..",
                "//div[contains(@class, 'layui-form-select')]//input[@placeholder='Please Select Country']/.."
            ]
            
            for selector in selectors:
                try:
                    country_selector = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    print(f"✅ 找到国家选择框: {selector}")
                    break
                except:
                    continue
            
            if not country_selector:
                print("❌ 未找到layui国家选择框")
                return False
            
            # 点击选择框展开选项
            country_selector.click()
            time.sleep(3)
            
            # 查找目标国家选项
            print(f"🔍 查找国家选项: {self.target_country}")
            
            # 等待下拉选项出现并重新查找
            try:
                country_options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//dd[contains(@class, '') and @lay-value]")))
                print(f"📋 找到 {len(country_options)} 个国家选项")
                
                # 查找匹配的国家选项
                target_option_value = None
                for option in country_options:
                    try:
                        option_text = option.text.strip()
                        if option_text == self.target_country:
                            target_option_value = option.get_attribute("lay-value")
                            print(f"✅ 找到精确匹配: {option_text} (value: {target_option_value})")
                            break
                        elif self.target_country.lower() in option_text.lower():
                            target_option_value = option.get_attribute("lay-value")
                            print(f"✅ 找到部分匹配: {option_text} (value: {target_option_value})")
                            break
                        # 特殊处理UAE的多种名称
                        elif self.target_country.upper() == "UAE" and ("emirates" in option_text.lower() or "uae" in option_text.lower()):
                            target_option_value = option.get_attribute("lay-value")
                            print(f"✅ 找到UAE匹配: {option_text} (value: {target_option_value})")
                            break
                    except:
                        continue
                
                if not target_option_value:
                    # 打印更多选项用于调试
                    print("📋 可用国家选项 (前20个):")
                    for i, option in enumerate(country_options[:20]):
                        try:
                            option_text = option.text.strip()
                            if option_text and option_text != "Please Select Country":
                                print(f"  {i+1}. {option_text}")
                        except:
                            print(f"  {i+1}. [无法读取]")
                    print(f"❌ 未找到匹配的国家选项: {self.target_country}")
                    print("💡 提示: 请从上面的列表中选择正确的国家名称")
                    return False
                
                # 重新查找并点击目标选项（使用lay-value属性）
                target_xpath = f"//dd[@lay-value='{target_option_value}']"
                target_option = wait.until(EC.element_to_be_clickable((By.XPATH, target_xpath)))
                target_option.click()
                time.sleep(3)
                print(f"✅ 已选择国家: {self.target_country}")
                
            except Exception as e:
                print(f"❌ 处理国家选项时出错: {e}")
                return False
            
            # 查找并点击搜索按钮
            print("🔍 查找搜索按钮...")
            search_selectors = [
                "//input[@type='submit']",
                "//button[@type='submit']", 
                "//button[contains(text(), 'Search')]",
                "//input[contains(@value, 'Search')]",
                "//a[contains(text(), 'Search')]"
            ]
            
            search_button = None
            for selector in search_selectors:
                try:
                    search_button = self.driver.find_element(By.XPATH, selector)
                    print(f"✅ 找到搜索按钮: {selector}")
                    break
                except:
                    continue
            
            if search_button:
                search_button.click()
                time.sleep(5)
                print(f"✅ 搜索完成")
                return True
            else:
                print("⚠️ 未找到搜索按钮，可能选择国家后会自动搜索")
                time.sleep(5)
                return True
            
        except Exception as e:
            print(f"❌ 搜索国家失败: {e}")
            # 保存页面截图用于调试
            try:
                self.driver.save_screenshot("debug_search_error.png")
                print("📸 已保存调试截图: debug_search_error.png")
            except:
                pass
            return False
    
    def extract_email(self, company_url, company_id):
        """提取企业邮箱"""
        try:
            print(f"  -> 访问详情页: {company_id}")
            
            # 保存当前窗口句柄
            main_window = self.driver.current_window_handle
            
            # 在新标签页中打开企业详情页
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 在新标签页中访问企业详情页
            self.driver.get(company_url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            # 检查是否需要登录
            if 'login' in self.driver.current_url.lower() or '登录' in page_text or 'Login' in page_text:
                print(f"  -> ⚠️ 需要登录，跳过此企业")
                # 关闭当前标签页并切换回主窗口
                self.driver.close()
                self.driver.switch_to.window(main_window)
                return ""
            
            # 提取邮箱
            email_patterns = [
                r'Office email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            email = ""
            for pattern in email_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    email = match.group(1)
                    print(f"  -> 📧 找到邮箱: {email}")
                    break
            
            if not email:
                print(f"  -> ❌ 未找到邮箱")
            
            # 关闭当前标签页并切换回主窗口
            self.driver.close()
            self.driver.switch_to.window(main_window)
            
            return email
            
        except Exception as e:
            print(f"  -> ❌ 错误: {e}")
            # 确保切换回主窗口
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(main_window)
            except:
                pass
            return ""
    
    def scrape_current_page(self, page_num=1, skip_companies=0):
        """抓取当前页面的企业数据"""
        print(f"\n📄 抓取第 {page_num} 页 (目标国家: {self.target_country})...")
        
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
                
                # 提取邮箱
                detail_url = f"https://glafamily.com/member/public/index/company/index.html?id={company_id}"
                email = self.extract_email(detail_url, company_id) if company_id else ""
                
                company_data = {
                    'country': self.target_country,
                    'company_name': name,
                    'email': email,
                    'company_id': company_id,
                    'detail_url': detail_url,
                    'scraped_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                companies.append(company_data)
                print(f"✅ {name} - 📧 {email if email else '无邮箱'}")
                
                # 立即保存到Excel（追加模式）
                self.append_to_excel([company_data])
                
                processed_count += 1
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                processed_count += 1
                continue
        
        return companies
    
    def navigate_to_page(self, page_num):
        """导航到指定页面"""
        try:
            print(f"🔄 尝试导航到第 {page_num} 页...")
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)
            time.sleep(2)  # 确保页面完全加载
            
            # 保存当前页面源码用于调试
            current_url = self.driver.current_url
            print(f"📍 当前URL: {current_url}")
            
            # 尝试多种翻页方式
            navigation_selectors = [
                f"//a[text()='{page_num}']",  # 直接页码链接
                f"//a[@href and contains(@href, 'page={page_num}')]",  # 包含page参数的链接
                f"//a[contains(@href, 'page') and text()='{page_num}']",  # 同时匹配href和文本
                "//a[contains(text(), '下一页') or contains(text(), 'Next') or text()='>']",  # 下一页按钮
                "//a[contains(@class, 'next') or contains(@class, 'page-next')]",  # 下一页按钮（通过class）
                "//li[contains(@class, 'next')]//a",  # 分页组件中的下一页
                "//div[contains(@class, 'pagination')]//a[contains(text(), '>')]",  # 分页容器中的下一页
                "//span[contains(@class, 'layui-laypage-next')]",  # layui下一页
                "//a[contains(@class, 'layui-laypage-next')]"  # layui下一页链接
            ]
            
            # 首先尝试直接页码链接
            for i, selector in enumerate(navigation_selectors[:3]):
                try:
                    print(f"  🔍 尝试选择器 {i+1}: {selector}")
                    page_link = self.driver.find_element(By.XPATH, selector)
                    if page_link.is_displayed() and page_link.is_enabled():
                        page_link.click()
                        time.sleep(3)
                        print(f"✅ 成功导航到第 {page_num} 页 (使用页码链接)")
                        return True
                    else:
                        print(f"  ⚠️ 元素不可见或不可点击")
                except Exception as e:
                    print(f"  ❌ 选择器失败: {e}")
                    continue
            
            # 如果页码链接不存在，尝试下一页按钮
            print("🔍 尝试下一页按钮...")
            for i, selector in enumerate(navigation_selectors[3:]):
                try:
                    print(f"  🔍 尝试下一页选择器 {i+1}: {selector}")
                    next_button = self.driver.find_element(By.XPATH, selector)
                    if next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        time.sleep(3)
                        print(f"✅ 成功导航到下一页 (使用下一页按钮)")
                        return True
                    else:
                        print(f"  ⚠️ 下一页按钮不可见或不可点击")
                except Exception as e:
                    print(f"  ❌ 下一页选择器失败: {e}")
                    continue
            
            # 如果都失败了，尝试查找所有可能的分页元素
            print("🔍 查找所有分页元素...")
            try:
                # 查找所有包含数字的链接
                page_links = self.driver.find_elements(By.XPATH, "//a[@href]")
                print(f"📋 找到 {len(page_links)} 个链接")
                
                valid_page_links = []
                for link in page_links:
                    try:
                        text = link.text.strip()
                        href = link.get_attribute('href') or ''
                        
                        # 检查是否为页码链接
                        if text.isdigit() and 1 <= int(text) <= 50:
                            valid_page_links.append((int(text), link, text, href))
                        elif 'page=' in href:
                            valid_page_links.append((0, link, text, href))
                        elif text in ['>', '下一页', 'Next', '»']:
                            valid_page_links.append((-1, link, text, href))
                    except:
                        continue
                
                print(f"📋 找到 {len(valid_page_links)} 个有效的分页链接:")
                for page_no, link, text, href in valid_page_links[:10]:  # 只显示前10个
                    print(f"  - 页码: {page_no}, 文本: '{text}', href: {href[:50]}...")
                
                # 尝试点击目标页码
                for page_no, link, text, href in valid_page_links:
                    if page_no == page_num:
                        try:
                            if link.is_displayed() and link.is_enabled():
                                link.click()
                                time.sleep(3)
                                print(f"✅ 成功导航到第 {page_num} 页")
                                return True
                        except:
                            continue
                
                # 如果找不到目标页码，尝试点击下一页
                for page_no, link, text, href in valid_page_links:
                    if page_no == -1:  # 下一页按钮
                        try:
                            if link.is_displayed() and link.is_enabled():
                                link.click()
                                time.sleep(3)
                                print(f"✅ 成功点击下一页")
                                return True
                        except:
                            continue
                        
            except Exception as e:
                print(f"❌ 查找分页元素失败: {e}")
            
            print(f"❌ 无法导航到第 {page_num} 页")
            return False
            
        except Exception as e:
            print(f"❌ 导航失败: {e}")
            return False
    
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
    
    def scrape_all_pages(self, max_pages=250):
        """抓取所有页面"""
        print(f"🎯 开始抓取 {self.target_country} 企业数据")
        print(f"📊 最大页数: {max_pages}")
        print(f"🔄 从第 {self.start_page} 页开始")
        
        # 首先搜索目标国家（只执行一次）
        if not self.search_by_country():
            print("❌ 无法搜索目标国家，退出抓取")
            return 0
        
        print("✅ 国家搜索完成，开始抓取企业数据...")
        
        # 获取总页数
        total_pages_detected = self.get_total_pages()
        print(f"🎯 目标: 抓取 {self.target_country} 的企业数据")
        print(f"📊 检测到总页数: {total_pages_detected} 页")
        print(f"📈 预计企业总数: {total_pages_detected * 12} 家 (每页约12家)")
        print(f"🔄 计划抓取页数: 第 {self.start_page} 页 到 第 {min(max_pages, total_pages_detected)} 页")
        print("=" * 60)
        
        total_found = 0
        consecutive_empty_pages = 0
        
        # 如果需要从特定页面开始，先导航到那一页
        if self.start_page > 1:
            print(f"🔄 导航到起始页面: 第 {self.start_page} 页")
            for page in range(2, self.start_page + 1):
                if not self.navigate_to_page(page):
                    print(f"❌ 无法导航到第 {page} 页")
                    return total_found
                time.sleep(2)
        
        # 开始抓取每一页
        current_page = self.start_page
        while current_page <= max_pages:
            try:
                print(f"\n📄 正在抓取第 {current_page} 页...")
                
                # 第一页可能需要跳过一些企业（断点续传）
                skip_companies = self.start_company if current_page == self.start_page else 0
                
                companies = self.scrape_current_page(current_page, skip_companies)
                
                if companies:
                    total_found += len(companies)
                    consecutive_empty_pages = 0
                    print(f"📈 第 {current_page} 页找到 {len(companies)} 家 {self.target_country} 企业")
                else:
                    consecutive_empty_pages += 1
                    print(f"📭 第 {current_page} 页没有找到企业")
                
                # 如果连续3页都没有企业，可能已经抓完了
                if consecutive_empty_pages >= 3:
                    print(f"🏁 连续 {consecutive_empty_pages} 页没有找到企业，停止抓取")
                    break
                
                # 重置起始位置（只在第一页有效）
                self.start_company = 0
                
                # 尝试导航到下一页
                current_page += 1
                if current_page <= max_pages:
                    print(f"🔄 准备翻到第 {current_page} 页...")
                    if not self.navigate_to_page(current_page):
                        print("🏁 无法导航到下一页，抓取结束")
                        break
                    time.sleep(2)  # 避免请求过快
                else:
                    print("🏁 已达到最大页数限制")
                    break
                
            except KeyboardInterrupt:
                print(f"\n⏹️ 用户中断，已保存到第 {current_page} 页")
                break
            except Exception as e:
                print(f"❌ 第 {current_page} 页抓取出错: {e}")
                # 出错时也尝试继续下一页
                current_page += 1
                continue
        
        print(f"\n🎉 抓取完成！总共找到 {total_found} 家 {self.target_country} 企业")
        return total_found
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()

    def get_total_pages(self):
        """获取总页数"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 查找分页信息的多种方式
            page_selectors = [
                '.pagination .page-item:last-child a',  # Bootstrap分页
                '.layui-laypage-last',  # layui分页
                '.page-numbers:last-child',  # 通用分页
                'a[href*="page="]:last-of-type',  # 包含page参数的链接
                '.pager a:last-child',  # 简单分页器
            ]
            
            total_pages = 1  # 默认至少1页
            
            for selector in page_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements:
                            text = element.get_text(strip=True)
                            if text.isdigit():
                                total_pages = max(total_pages, int(text))
                                print(f"✅ 从选择器 '{selector}' 找到页数: {text}")
                except:
                    continue
            
            # 如果上面的方法都没找到，尝试查找所有包含数字的链接
            if total_pages == 1:
                try:
                    # 查找所有可能的页码链接
                    page_links = soup.find_all('a', href=True)
                    page_numbers = []
                    
                    for link in page_links:
                        text = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        # 检查链接文本是否为数字
                        if text.isdigit() and 1 <= int(text) <= 100:  # 合理的页数范围
                            page_numbers.append(int(text))
                        
                        # 检查href中的page参数
                        if 'page=' in href:
                            try:
                                import re
                                match = re.search(r'page=(\d+)', href)
                                if match:
                                    page_numbers.append(int(match.group(1)))
                            except:
                                pass
                    
                    if page_numbers:
                        total_pages = max(page_numbers)
                        print(f"✅ 从页码链接分析得到总页数: {total_pages}")
                        print(f"📋 找到的页码: {sorted(set(page_numbers))}")
                
                except Exception as e:
                    print(f"⚠️ 分析页码链接时出错: {e}")
            
            print(f"📊 检测到总页数: {total_pages}")
            return total_pages
            
        except Exception as e:
            print(f"❌ 获取总页数失败: {e}")
            return 1

def run_country_scraper(country_name):
    """运行指定国家的爬虫"""
    print(f"🌍 GLA Family {country_name} 企业邮箱抓取器")
    print("=" * 60)
    print(f"🎯 目标国家: {country_name}")
    print("✨ 支持断点续传，自动追加到Excel文件")
    print("📊 将抓取所有可用页面")
    print()
    
    scraper = CountryScraper(country_name)
    
    try:
        # 开始抓取
        total_found = scraper.scrape_all_pages()
        
        if total_found > 0:
            print(f"\n📊 最终统计:")
            print(f"   - Excel文件: {scraper.excel_filename}")
            print(f"   - 企业数量: {total_found} 家")
            print(f"   - 目标国家: {country_name}")
        else:
            print(f"\n😔 未找到 {country_name} 的企业数据")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断抓取")
    except Exception as e:
        print(f"❌ 抓取过程中出错: {e}")
    finally:
        scraper.close()
    
    return total_found 