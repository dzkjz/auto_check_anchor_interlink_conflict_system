from datetime import datetime
import json
import os
import pathlib
import re
import time

import pymysql

from browser.useragent import ran_user_agent_desktop
from db_handler import database_handler
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Tuple
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver as seDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
import lxml.html
import lxml.html.clean
from threading import Thread, Barrier


def analysis_text(eles: List, anchor: str):
    conflict = False
    for ele in eles:
        text: str = ele.text
        text = text.replace(" " + anchor + " ", "")
        text = text.replace(" " + anchor, "")
        text = text.replace(anchor + " ", "")
        if anchor in text:
            conflict = True
        else:
            conflict = False
    return conflict


def analysis_content_text(text: str, anchor: str, need_content=False) -> Tuple[bool, list]:
    # 有符号的可以加，移除掉看看还有没有不是前后符号或者空白换行的
    # text = re.sub(rf'''[\s\W]{anchor}[\s\W]''', '', text)
    text = text.replace(" " + anchor + " ", "")
    text = text.replace("(" + anchor + ")", "")

    # text = text.replace(" " + anchor, "")
    # text = text.replace("-" + anchor, "") #币对词
    text = text.replace(" (" + anchor, "")
    # text = text.replace('/' + anchor, "")  # 币对词

    # text = text.replace(anchor + " ", "")
    # text = text.replace(anchor + "-", "") #币对词
    text = text.replace(anchor + ")", "")
    # text = text.replace(anchor + "/", "")  # 币对词

    text = text.replace("&nbsp;", ' ')
    # 看移除了前后符号空白换行之后的，还有没有文本包含这个anchor
    conflict = False
    conflictws = []
    if anchor in text:
        # 冲突词
        # conflict_words = re.match(rf"(?=\w*({anchor}))\w+", text)
        # for conflict_word in conflict_words:
        #     if conflict_word.strip() not in conflictws:
        #         conflictws.append(conflict_word.strip())
        # 前后有文字的
        re_rule = fr'(?:[\w|\-|\/]*){anchor}(?:[\w|\-|\/]*)'
        conflict_words = re.findall(re_rule, text)
        for conflict_word in conflict_words:
            conflict_word = conflict_word.strip().lower()
            if not conflict_word == anchor.strip().lower():
                if conflict_word not in conflictws:
                    conflictws.append(conflict_word)
        if need_content:
            print(text)
        # 全一样文本的【即自身】不算冲突
        if anchor in conflictws:
            conflictws.remove(anchor)
        for conflictw in conflictws:
            print(conflictw + "冲突")
            conflict = True
            # print(conflict_word.group() + f"不与{anchor}冲突")
    else:
        conflict = False
    return conflict, conflictws


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


def source_parse_to_text():
    dh = database_handler()
    res = dh.read_article_content_urls()
    urls = []
    for re in res:
        urls.append(re[0])
    results = dh.read_article_source_code_except_urls(urls)
    # driver = initialize_driver()
    for result in results:
        id = result[0]
        url = result[1]
        parent_url = result[2]
        source_code: str = result[3]

        # temp_location = os.path.dirname(os.path.abspath(__file__)) + "/temp/temp.html"
        # with open(temp_location, 'wb+') as f:
        #     f.write(source_code.encode())
        # url_parsed = pathlib.Path(temp_location).as_uri()
        # driver.get(url_parsed)

        # todo 需要移除的标签
        def removeTagFromHtml(selectors: List[str], driver: WebDriver) -> WebDriver:
            for selector in selectors:
                driver.execute_script("""
                                                                            var elements = document.querySelectorAll(""" + "'" + selector + "'" + """);
                                                                                    if (elements.length>0){
                                                                                    elements.forEach(function(ele){
                                                                                        ele.parentNode.removeChild(ele)
                                                                                    })}
                                                                            """)
            return driver

        # driver = removeTagFromHtml(['a', 'br'], driver)

        # todo 需要替换的标签
        def replaceTagFromHtml(selectors: List[str], driver: WebDriver) -> WebDriver:
            for selector in selectors:
                driver.execute_script("""
                                                                            var elements = document.querySelectorAll(""" + "'" + selector + "'" + """);
                                                                                    if (elements.length>0){
                                                                                    elements.forEach(function(ele){
                                                                                        ele.innerText = " "+ele.innerText+" "
                                                                                    })}
                                                                            """)
            return driver

        # driver = replaceTagFromHtml(['td', 'span', 'b', 'p', 'li'], driver)

        def removeHtmlTag(selectors: List[str], source_code: str):
            for selector in selectors:
                soup = BeautifulSoup(source_code, 'html.parser')
                tags = soup.select(selector)
                tags.reverse()
                for tag in tags:
                    tag.extract()
                source_code = str(soup)
            return source_code

        def replaceHtmlTag(source_code: str):
            soup = BeautifulSoup(source_code, 'html.parser')
            tags = soup.findAll()
            tags.reverse()

            for tag in tags:
                if tag.string:
                    tag.string.replace_with(f" {tag.string} ")
                    tag.text.replace(" ", ' ')
                    tag.text.replace("\n", " ").replace("\r", " ").replace("\r\n", " ")
                    tag.text.replace(" ", ' ')
                    tag.text.replace(u"\xa0", ' ')
                    tag.text.replace("&nbsp;", ' ')
                    tag.text.replace(u"\u2022", " ")
            source_code = str(soup)

            return source_code

        source_code = removeHtmlTag(['a', 'br'], source_code)
        source_code = replaceHtmlTag(source_code)
        # todo td需要对单元格内的文本前后加空格

        soup = BeautifulSoup(source_code, 'html.parser')
        ele = soup.select_one('div[class*="kucoin-article"]')
        ele_source = str(ele)
        if len(ele.text.strip()) > 0:
            ele_source = lxml.html.fromstring(ele_source)
            cleaner = lxml.html.clean.Cleaner(style=True)
            ele_source = cleaner.clean_html(ele_source).text_content()
            soup = BeautifulSoup(ele_source, 'html.parser')
            content = soup.text
        else:
            content = ele.text
        content = content.replace(" ", ' ')
        content = content.replace("\n", " ").replace("\r", " ").replace("\r\n", " ")
        content = content.replace(" ", ' ')
        content = content.replace(u"\xa0", ' ')
        content = content.replace("&nbsp;", ' ')
        # content = content.encode().decode('utf-8').replace(u"\u2022", " ")
        print(f"处理第{id}篇")
        dh.save_article_content_text(url, parent_url, content)


def get_anchors():
    anchor_file = 'anchors.txt'
    acs = []

    if os.path.exists(anchor_file):
        with open(anchor_file, 'r') as f:
            acs = f.readlines()
    anchors = []
    for a in acs:
        anchor = a.strip()
        anchors.append(anchor)
    return anchors


def start(no_save_to_database=True, new_anchor_list_need_empty_database=True):
    source_parse_to_text()
    # threads = []
    # max_threads = 1
    # for i in range(max_threads):
    #     t = Thread(target=source_parse_to_text)
    #     time.sleep(1)
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()

    anchors = get_anchors()

    # 检测是否anchors冲突

    # 是否与其他币种冲突【同名】

    dh = database_handler()
    if new_anchor_list_need_empty_database:
        dh.drop_anchors_conflict_url_words_table()
        dh.create_anchors_conflict_url_words_table()
    # 检测源码中是否有文本
    for anchor in anchors:
        anchor = anchor.strip()
        print(f"检测{anchor}")
        anchor_to_check = anchor.lower().strip()
        conflicted = False
        source_contents = dh.read_article_content_like_anchor(anchor=anchor_to_check)
        for source_content in source_contents:
            p_content = source_content[3]
            p_content = p_content.lower()
            # 文本是否前后非空格【有空格视作OK，没空格，视作冲突，标注冲突URL，由手动添加】
            result = analysis_content_text(p_content, anchor_to_check)
            conflict = result[0]
            if conflict:
                # 标注冲突URL，由手动添加
                conflicted_url = source_content[1]
                print(f"标注冲突URL:{conflicted_url} ，由手动添加{anchor}")
                conflicted = conflict
                conflicted_words = result[1]
                conflicted_words = json.dumps(conflicted_words)
                if not no_save_to_database:
                    dh.save_anchors_conflict_url_words(conflicted_url, anchor, conflicted_words, datetime.now())
        if not conflicted:
            print(f"{anchor}未发现冲突页面,可以自动链接")

    # DAO 与 H2O DAO 【如果被其他币种包含，则视为冲突】此情况很难，因为H2O DAO锚文本是H2O 所以自动添加时只会添加H2O，如果某币种全包含，则短币自动
    # 会排除掉，也就不用考虑了


def conflict_filter(no_save_to_database=True):
    dh = database_handler()

    anchors = get_anchors()
    # 哪些币在哪个页面存在冲突 冲突文本是什么【已解决】
    # 冲突文本是否是会优先匹配到更长设定文本 如果是，那更长设定文本会不会也会出问题【包含在word中】 不会->ok 都不冲突 会->标注更长设定文本会冲突
    # 如果不会匹配更长设定文本，标注本文本冲突
    for anchor_outer in anchors:
        for anchor_inner in anchors:
            if anchor_outer in anchor_inner and anchor_outer != anchor_inner:
                print(f"{anchor_inner} 覆盖了 {anchor_outer}")
                # 需要看看这个更长的anchor_inner是否在anchor_outer的冲突值中会不会也会出问题【包含在word中】
                anchor_outer_conflicted_datas = dh.read_anchors_conflict_url_words(anchor_outer)
                for anchor_outer_conflicted_data in anchor_outer_conflicted_datas:
                    anchor_outer_conflicted_data_words: List[str] = \
                        anchor_outer_conflicted_data[3].replace('[', '').replace(']', '').replace("\"", "").split(',')
                    print(f'检查{anchor_inner}是否存在于{anchor_outer_conflicted_data_words}当中')
                    if anchor_inner.lower() in anchor_outer_conflicted_data_words:
                        # 出现过 会冲突；
                        anchor_outer_conflicted_id = anchor_outer_conflicted_data[0]
                        print(
                            f'{anchor_outer_conflicted_id} {anchor_outer_conflicted_data_words}中出现过{anchor_inner}，会冲突')
                        # 移除anchor_outer中的冲突值,如果为0 则移除整个row
                        anchor_outer_conflicted_data_words.remove(anchor_inner.lower())
                        print(f"移除{anchor_inner}后：{anchor_outer_conflicted_data_words}")
                        if not no_save_to_database:
                            if len(anchor_outer_conflicted_data_words) < 1:
                                # 直接删除该row
                                dh.del_anchors_conflict_url_words_row(anchor_outer_conflicted_id)
                            else:
                                anchor_outer_conflicted_data_new_words = json.dumps(anchor_outer_conflicted_data_words)

                                dh.update_anchors_conflict_url_words(anchor_outer_conflicted_id,
                                                                     str(anchor_outer_conflicted_data_new_words),
                                                                     datetime.now())


start(no_save_to_database=False, new_anchor_list_need_empty_database=True)
conflict_filter(no_save_to_database=False)
