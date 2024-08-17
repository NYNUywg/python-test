from playwright.sync_api import sync_playwright


def get_index_context():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://www.jctrans.com/cn/home/963d2723459700775661af809ad2a1d9')  # 将网址替换为目标网站的网址

        # 等待页面加载完成
        page.wait_for_load_state('networkidle')

        # 获取动态生成的内容
        dynamic_content = page.inner_html('body')

        # 获取公司
        h1_elements = page.locator('h1').all()
        company = h1_elements[2].inner_text()
        print(company)
        # 获取邮箱
        flex_elements = page.locator('.content').all()
        email = flex_elements[len(flex_elements) - 2].inner_text()
        print(email)
        browser.close()
