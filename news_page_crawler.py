# todo 看内容的文本里面是什么
# 是否包含这个关键词
# 这个关键词的句子是什么
import json
import random
import re
import time
from datetime import datetime
from typing import List, Tuple
from bs4 import BeautifulSoup

from selenium import webdriver as seDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
from urllib.parse import unquote
from threading import Thread, Barrier
import db_handler
from browser.useragent import ran_user_agent_desktop
import os.path
from db_handler import database_handler


class driver_index:
    def __init__(self, id: int, driver: WebDriver):
        self.__driver__: WebDriver = driver
        self.__id__: int = id

    def set_id(self, id: int):
        self.__id__ = id

    def get_id(self) -> int:
        return self.__id__

    def set_driver(self, driver: WebDriver):
        self.__driver__ = driver

    def get_driver(self) -> WebDriver:
        return self.__driver__


class crawler:

    def __init__(self, lang=None):
        """可以设置国家 设置格式 en-US"""
        self.__driver_options__ = None
        self.__driver__: WebDriver

        self.__lang__ = lang
        self.__device__ = 'desktop'
        self.__keyword__ = ''
        self.__ua_string__ = ''
        # self.__log_path__ = path

    def __page_has_loaded__(self):
        wait = WebDriverWait(self.__driver__, 20, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div')))
        page_state = ''
        try:
            page_state = self.__driver__.execute_script('return document.readyState;')
        finally:
            return page_state == 'complete'

    def __device_switcher__(self):
        self.__device__ = 'desktop'

        """BlackBerry Z30,
        LG Optimus L70,
        Microsoft Lumia 950,
        Nexus 10,
        iPhone 4,
        Galaxy S5,
        iPhone 6 Plus,
        iPad,
        """

        if self.__ua_string__.find('Android') > -1 or self.__ua_string__.find('iPhone') > -1:
            self.__device__ = 'mobile'
            mobile_emulation = {
                "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
                "userAgent": self.__ua_string__}
            self.__driver_options__.add_experimental_option('mobileEmulation', mobile_emulation)

    def __headless__(self, headless):
        # 设置无头浏览器
        if headless:
            self.__driver_options__.add_argument('--headless')
            self.__driver_options__.add_argument('--disable-gpu')

    def __lang_switcher__(self):
        # 切换语言
        if self.__lang__ is None:
            # lang_list = self.__lang_list__
            # self.__lang__ = random.choice(lang_list).strip()
            self.__lang__ = "en-GB"
        self.__driver_options__.add_experimental_option('prefs', {'intl.accept_languages': f'{self.__lang__}'})

    def __ua_switcher__(self):
        self.__ua_string__ = ran_user_agent_desktop()
        self.__driver_options__.add_argument(f"--user-agent={self.__ua_string__}")
        print(f"使用ua： {self.__ua_string__}")

    def initialize_driver(self) -> WebDriver:
        driver_options = seDriver.ChromeOptions()
        """开启无头与否"""
        # 修改 UA 信息
        ua_string = ran_user_agent_desktop()
        driver_options.add_argument(f"--user-agent={ua_string}")
        driver_options.add_experimental_option('prefs', {'intl.accept_languages': "en-GB"})
        # 设置无头浏览器
        driver_options.add_argument('--headless')
        driver_options.add_argument('--disable-gpu')

        # 配置chrome 浏览器
        s = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = seDriver.Chrome(service=s, options=driver_options)
        return driver

    def get_article_urls_in_pagenation(self, pagenation_url, articles, driver: WebDriver):
        t_start = datetime.now()
        driver.get(pagenation_url)
        time.sleep(0.2)
        self.page_has_loaded(driver)
        t_end = datetime.now()
        print(f"用时{(t_end - t_start).seconds}秒")
        articles_on_page = driver.find_elements(By.CSS_SELECTOR,
                                                'div[class*="mainWrapper"] [class*="main"] a:not([href*="/search/"])')

        for article in articles_on_page:
            article_url = article.get_attribute('href')
            if article_url not in articles:
                # 存表
                db = db_handler.database_handler()
                db.save_article_urls(article_url, pagenation_url, datetime.now())

    def __pull_news_result__(self, multingual=False):
        # 获取页面数量
        if multingual:
            language_list = [
                '/de',
                '/es',
                '/fr',
                '/ko',
                '/nl',
                '/pt',
                '/tr',
                '/vi',
                'zh-hans',
                'zh-hant',
                '/it',
                '/id',
                '/ms',
                '/hi',
                '/th',
                '/ja',
                '/bn',
                '/pl',
                '/fil',
                '/ru',
            ]
            base_url = 'https://www.kucoin.com'
            path = '/news'
            entry_url_news = []
            for language in language_list:
                entry_url_news.append(base_url + language + path)
        else:
            entry_url_new = 'https://www.kucoin.com/news'
            self.get_articles_url_of_all(index_page=entry_url_new)

    def get_pagenation_total(self, index_page: str):
        selector_pagination = 'li[data-item="page"]'
        self.__driver__.get(index_page)
        self.__page_has_loaded__()
        pages = self.__driver__.find_elements(By.CSS_SELECTOR, selector_pagination)
        all_page_counts = int(pages[len(pages) - 1].text)
        print(all_page_counts)
        self.__driver__.quit()
        return all_page_counts

    def get_articles_url_of_all(self, index_page: str):
        dh = database_handler()
        all_pagenations = []
        all_page_counts = self.get_pagenation_total(index_page=index_page)

        for index in range(all_page_counts):
            index += 1
            news_pagination_url = index_page + f"/{index}"
            # 收集到列表中
            all_pagenations.append(news_pagination_url)

        # 多线程处理
        articles = []

        driver_ids: List[driver_index] = []
        max_number_of_threads = 10  # 调整线程数量
        # 准备浏览器
        if len(driver_ids) < max_number_of_threads:
            for d in range(max_number_of_threads - len(driver_ids)):
                driver = self.initialize_driver()
                di = driver_index(id=d + 1, driver=driver)
                driver_ids.append(di)
        # 分配浏览器执行抓取
        all_pagenations_to_crawl = all_pagenations
        while len(all_pagenations_to_crawl) > 0:
            # 如果还有页面待抓取
            if len(all_pagenations_to_crawl) >= max_number_of_threads:
                # 剩余待抓页面比线程容量大 [暂时只用线程容量去分配浏览器]
                max_number_of_threads = max_number_of_threads
            else:
                # 剩余的不多了，只需要给一小部分容量的浏览器
                max_number_of_threads = len(all_pagenations_to_crawl)
            # 抓排在前面的
            pagenations = all_pagenations_to_crawl[0:max_number_of_threads]
            # 移除已经加入到待抓列表里的
            del all_pagenations_to_crawl[0:max_number_of_threads]

            threads = []

            # 依次分配
            for pagenation in pagenations:
                id = pagenations.index(pagenation)
                driver = driver_ids[id].get_driver()
                print(f'Use {id} browser,id is {driver_ids[id].get_id()} to Crawl {pagenation}')
                t = Thread(target=self.get_article_urls_in_pagenation, args=(pagenation, articles, driver))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()

            # 检查是否有未抓取页面
            article_datas = dh.read_article_urls()
            ad = []
            for article_data in article_datas:
                ad.append(article_data[2])
            leaved_aus = list(set(all_pagenations) - set(ad))
            # 设置剩余未抓取页面为待抓页面
            all_pagenations_to_crawl = leaved_aus

        print("退出浏览器")
        for driver_id in driver_ids:
            driver_id.get_driver().quit()

    def page_has_loaded(self, driver: WebDriver):
        wait = WebDriverWait(driver, 20, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div')))
        page_state = ''
        try:
            page_state = driver.execute_script('return document.readyState;')
        finally:
            return page_state == 'complete'

    def continuous_start(self, headless=True, multingual=False):
        self.__driver_options__ = seDriver.ChromeOptions()

        """开启无头与否"""
        # 切换语言
        self.__lang_switcher__()

        # 修改 UA 信息
        self.__ua_switcher__()
        # 切换设备
        # self.__device_switcher__()
        # 设置无头浏览器
        self.__headless__(headless)

        # 配置chrome 浏览器
        s = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

        self.__driver__ = seDriver.Chrome(service=s, options=self.__driver_options__)
        # 爬news页面
        self.__pull_news_result__(multingual=multingual)
        # 退出
        self.__driver__.quit()

    def pull_source_code(self):
        dh = database_handler()
        auds = dh.read_article_urls()
        aus = []

        class article:
            def __init__(self, url: str, parent_url: str):
                self.__url__ = url
                self.__parent_url__ = parent_url

            def get_url(self):
                return self.__url__

            def get_parent_url(self):
                return self.__parent_url__

        for aud in auds:
            ar = article(aud[1], aud[2])
            aus.append(ar)

        # 多线程处理
        def initialize_driver() -> WebDriver:
            driver_options = seDriver.ChromeOptions()
            """开启无头与否"""
            # 修改 UA 信息
            ua_string = ran_user_agent_desktop()
            driver_options.add_argument(f"--user-agent={ua_string}")
            driver_options.add_experimental_option('prefs', {'intl.accept_languages': "en-GB"})
            # 设置无头浏览器
            driver_options.add_argument('--headless')
            driver_options.add_argument('--disable-gpu')

            # 配置chrome 浏览器
            s = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = seDriver.Chrome(service=s, options=driver_options)
            return driver

        driver_ids: List[driver_index] = []
        max_number_of_threads = 10  # 调整线程数量
        if len(driver_ids) < max_number_of_threads:
            for d in range(max_number_of_threads - len(driver_ids)):
                driver = initialize_driver()
                di = driver_index(id=len(driver_ids) + 1, driver=driver)
                driver_ids.append(di)

        # 从aus中取线程数量的文章去爬取
        aus_copy = aus
        while len(aus_copy) > 0:
            if len(aus_copy) >= max_number_of_threads:
                max_number_of_threads = max_number_of_threads
            else:
                max_number_of_threads = len(aus_copy)
            auts = aus_copy[0:max_number_of_threads]
            del aus_copy[0:max_number_of_threads]

            threads = []

            for aut in auts:
                id = auts.index(aut)
                driver = driver_ids[id].get_driver()
                driver_working = True
                try:
                    title = driver.title
                except WebDriverException:
                    driver_working = False
                if not driver_working:
                    driver = initialize_driver()
                    driver_ids[id].set_driver(driver)

                print(f'Use {id} browser,id is {driver_ids[id].get_id()} to Crawl {aut.get_url()}')
                t = Thread(target=self.pull_news_page_details_source_code,
                           args=(driver, aut.get_url(), aut.get_parent_url()))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

            # 检查是否有未抓取页面
            dh = database_handler()
            rascus = dh.read_article_source_code_urls()
            ascus = []
            for rascu in rascus:
                ascus.append(rascu[0])

            leaved_ascus = []
            for au in aus:
                if au.get_url() not in ascus:
                    leaved_ascus.append(au)
            # 设置剩余未抓取页面为待抓页面
            aus_copy = leaved_ascus

        for driver_id in driver_ids:
            driver_id.get_driver().quit()

    def pull_news_page_details_source_code(self, driver: WebDriver, article_url: str, parent_url: str):
        def page_has_content(driver: WebDriver, content_flag='div[class*="kucoin-article"]'):
            eles = driver.find_elements(By.CSS_SELECTOR, content_flag)
            return len(eles) > 0

        def page_has_loaded(driver: WebDriver):
            wait = WebDriverWait(driver, 20, poll_frequency=1,
                                 ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div')))
            page_state = ''
            try:
                page_state = driver.execute_script('return document.readyState;')

            finally:
                return page_state == 'complete'

        print("抓取页面源码")
        t_start = datetime.now()
        driver.get(article_url)
        page_has_loaded(driver)
        time.sleep(0.2)

        if not page_has_content(driver):
            return

        # 剔除svg
        def excludeTagFromWebDriver(driver: WebDriver, selector: str):
            js = """
                var elements = document.querySelectorAll(""" + "'" + selector + "'" + """);
                if (elements.length>0){
                elements.forEach(function(ele){
                ele.parentNode.removeChild(ele)})}"""
            driver.execute_script(js)
            return driver

        driver = excludeTagFromWebDriver(driver, "svg")  # 这个太长了
        driver = excludeTagFromWebDriver(driver, "script")
        driver = excludeTagFromWebDriver(driver, "style")
        driver = excludeTagFromWebDriver(driver, 'link[rel="stylesheet"]')
        t_end = datetime.now()
        print(f"用时{(t_end - t_start).seconds}秒")
        # driver.execute_script()
        # 获取剔除svg后的pagesource
        page_source = driver.page_source

        dh = database_handler()
        dh.save_article_source_code(article_url, parent_url, page_source, t_end)
