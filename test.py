from selenium import webdriver
from selenium.webdriver.common.by import By

# https://www.jctrans.com/
# 账户：jane111
# 密码：HIPPO123

# 创建一个Chrome浏览器实例
driver = webdriver.Chrome()

# 打开网页
url = 'https://www.bilibili.com/v/popular/rank/all/'
driver.get(url)

# 查找<ul class="rank-list">下的所有<li class="rank-item">
rank_items = driver.find_elements(By.CSS_SELECTOR, 'ul.rank-list li.rank-item')

# 打印每个<li class="rank-item">的内容
for rank_item in rank_items:
    # 获取<li class="rank-item">元素中的data-rank属性值
    data_rank_value = rank_item.get_attribute('data-rank')
    print(data_rank_value)
    # 在每个<li class="rank-item">元素中查找<a class="title">元素
    info_element = rank_item.find_element(By.CSS_SELECTOR, 'a.title')
    print(info_element.text)

# 关闭浏览器
# driver.quit()