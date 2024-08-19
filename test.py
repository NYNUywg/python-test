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
