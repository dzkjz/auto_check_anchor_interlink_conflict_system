import random
import re
import time
from datetime import datetime
from typing import List

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

import db_handler
from browser.useragent import ran_user_agent_desktop
import os.path
from db_handler import database_handler


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

    def __pull_price__(self, coin_ticker):
        gurl = 'https://www.kucoin.com/price/'
        self.__coin_ticker__ = coin_ticker
        self.__price_url__ = gurl + coin_ticker
        print(f"打开{self.__price_url__}")
        self.__driver__.get(self.__price_url__)
        self.__page_has_loaded__()
        time.sleep(1)

    def __get_coin_anchor__(self, coin_ticker):
        db = db_handler.database_handler()
        self.__pull_price__(coin_ticker)
        self.__coin_anchor__ = self.__driver__.find_element(By.CSS_SELECTOR, '[data-ssg="coin-info-title"]').text
        self.__coin_anchor__ = self.__coin_anchor__.replace(" Info", "")
        print(f'网址:{self.__price_url__},币种:{coin_ticker},锚文本:{self.__coin_anchor__}')
        db.save_coin_anchors_data(url=self.__price_url__, coin_anchors=self.__coin_anchor__, coin_ticker=coin_ticker)

    def continuous_start(self, headless=True):
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
        # 获取coins
        coins = self.__read_coins__()
        # 找coinname
        for coin in coins:
            coin = coin.strip()
            print(f"找:{coin}")
            self.__get_coin_anchor__(coin_ticker=coin)
        # 退出
        self.__driver__.quit()

    def __read_coins__(self):
        coins = []
        if os.path.exists("coins.txt"):
            data = open("coins.txt", "r")
            coins = data.readlines()

        return coins
