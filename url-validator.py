from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
import random
import time
import json
from urls import urls
from Excel_Initializer import ExcelInitializer


class SitemapURLValidator:

    def page_has_loaded(self, driverWeb: WebDriver):
        wait = WebDriverWait(driverWeb, 20, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//div')))
        # print("Checking if {} page is loaded.".format(currentUrl))
        page_state = ''
        try:
            page_state = driverWeb.execute_script('return document.readyState;')
        finally:
            return page_state == 'complete'

    def start(self, headless=False):
        # 切换语言
        options = webdriver.ChromeOptions()
        # 设置无头浏览器
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        # 配置chrome 浏览器
        # s = Service(ChromeDriverManager().install())
        s = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=s, options=options)
        # 打开页面
        for url in urls:
            driver.get(url)
            time.sleep(3)
            try:
                print('转到页面')
                if self.page_has_loaded(driver):  # 等待页面打开
                    now_url = driver.current_url
                    print('页面已经打开: {}'.format(now_url))
                    self.save_to_excel(original_url=url, corrected_url=now_url)
            except TimeoutException:
                print('页面打开超时！继续下一个...')

            except WebDriverException:
                print('页面打开错误:{}'.format(WebDriverException.args))

            finally:
                print("检测完成！")

        driver.quit()

    def save_to_excel(self, original_url, corrected_url):
        # excel初始化
        excel = ExcelInitializer()
        # 新插入一行
        excel.NewRow(original_url, corrected_url)

    def duplicate_check(self, original_url, corrected_url):
        # excel初始化
        excel = ExcelInitializer()
        # 检测重复
        return excel.DuplicateCheck(original_url, corrected_url)


sv = SitemapURLValidator()
sv.start()
