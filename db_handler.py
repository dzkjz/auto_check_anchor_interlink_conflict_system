import decimal

from mysql.connector import connect, Error
import datetime
from typing import List
import os
from pandas import json_normalize
import json


class database_handler:
    def __init__(self):
        self.__host__ = "localhost"
        self.__user__ = "root"
        self.__password__ = "12345678"
        self.__database_name__ = 'backlinks_tracker'

    def __execute_query__(self, query, parameters, need_result: bool, save_rowid: bool, database='backlinks_tracker'):
        try:
            with connect(host=self.__host__, user=self.__user__, password=self.__password__,
                         database=database) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, parameters)
                    if save_rowid:
                        result = cursor.lastrowid
                        connection.commit()
                        return result
                    if need_result:
                        result = cursor.fetchall()
                        connection.commit()
                        return result

                    connection.commit()
        except Error as e:
            connection.rollback()
            print(f"Error database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def save_coin_anchors_data(self, url: str, coin_anchors: str, coin_ticker: str):

        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id FROM price_coin_anchor.coin_anchors where price_url=%s'''
        result = self.__execute_query__(select_query, (url,), True, False)
        if len(result) > 0:
            return
        # 插入新记录
        save_query = f'''INSERT IGNORE INTO price_coin_anchor.coin_anchors(coin_ticker, coin_anchor, price_url) VALUES (%s,%s,%s) '''
        self.__execute_query__(save_query, (coin_ticker, coin_anchors, url), False, False)

    def save_article_urls(self, url: str, parent_url: str, crawled_time: datetime):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id FROM news_pages.article_urls where url=%s'''
        result = self.__execute_query__(select_query, (url,), True, False)
        if len(result) > 0:
            return
        # 插入新记录
        save_query = f'''INSERT IGNORE INTO news_pages.article_urls( url, parent_url, crawled_time) VALUES (%s,%s,%s) '''
        self.__execute_query__(save_query, (url, parent_url, crawled_time), False, False)

    def read_article_urls(self):
        select_query = f'''SELECT id, url, parent_url, crawled_time FROM news_pages.article_urls'''
        result = self.__execute_query__(select_query, (), True, False)
        return result

    def save_article_source_code(self, url: str, parent_url: str, sourcecode: str, crawled_time: datetime):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id FROM news_pages.pages_source_code where url=%s'''
        result = self.__execute_query__(select_query, (url,), True, False)
        if len(result) > 0:
            return
        # 插入新记录
        save_query = f'''INSERT IGNORE INTO news_pages.pages_source_code(url, parent_url,source_code,crawled_time) VALUES (%s,%s,%s,%s) '''
        self.__execute_query__(save_query, (url, parent_url, sourcecode, crawled_time), False, False)

    def read_article_source_code_urls(self):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT url FROM news_pages.pages_source_code'''
        result = self.__execute_query__(select_query, (), True, False)
        return result

    def read_article_source_code(self):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id, url, parent_url, source_code, crawled_time FROM news_pages.pages_source_code '''
        result = self.__execute_query__(select_query, (), True, False)
        return result

    def read_article_source_code_except_urls(self, urls):
        # 检查是否已经插入过该条记录
        if len(urls) > 0:
            select_query = f'''SELECT id, url, parent_url, source_code, crawled_time FROM news_pages.pages_source_code 
                    where url not in (%s)'''
            in_p = ', '.join(list(map(lambda x: '%s', urls)))
            select_query = select_query % in_p
            result = self.__execute_query__(select_query, urls, True, False)
        else:
            select_query = f'''SELECT id, url, parent_url, source_code, crawled_time FROM news_pages.pages_source_code'''
            result = self.__execute_query__(select_query, (), True, False)
        return result

    def read_article_source_code_like_anchor(self, anchor: str):
        anchor = anchor.lower()
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id, url, parent_url, lower(source_code), crawled_time 
        FROM news_pages.pages_source_code 
        WHERE lower(source_code) like %s
        '''
        result = self.__execute_query__(select_query, ("%{}%".format(anchor),), True, False)
        return result

    def save_article_content_text(self, url, parent_url, content_text):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id FROM news_pages.article_content where url=%s'''
        result = self.__execute_query__(select_query, (url,), True, False)
        if len(result) > 0:
            return
        # 插入新记录
        save_query = f'''INSERT IGNORE INTO news_pages.article_content(url, parent_url,content) VALUES (%s,%s,%s) '''
        self.__execute_query__(save_query, (url, parent_url, content_text), False, False)

    def read_article_content_urls(self):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT url FROM news_pages.article_content'''
        result = self.__execute_query__(select_query, (), True, False)
        return result

    def read_article_content_like_anchor(self, anchor: str, is_regex=False):
        anchor = anchor.lower()

        if is_regex:
            select_query = f'''SELECT id, url, parent_url, lower(content)
                    FROM news_pages.article_content
                    WHERE lower(content) rlike %s
                    '''
            result = self.__execute_query__(select_query, (anchor,), True, False)
        else:
            select_query = f'''SELECT id, url, parent_url, lower(content)
                    FROM news_pages.article_content
                    WHERE lower(content) like %s
                    '''
            result = self.__execute_query__(select_query, ("%{}%".format(anchor),), True, False)
        return result

    def save_anchors_conflict_url_words(self, url: str, anchor: str, conflict_words: str, checked_time: datetime):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id FROM news_pages.anchors_conflict_url_words where anchor=%s and url=%s'''
        result = self.__execute_query__(select_query, (anchor, url,), True, False)
        if len(result) > 0:
            return
        # 插入新记录
        save_query = f'''INSERT IGNORE INTO news_pages.anchors_conflict_url_words(url, anchor, words,checked_time) VALUES (%s,%s,%s,%s) '''
        self.__execute_query__(save_query, (url, anchor, conflict_words, checked_time), False, False)

    def read_anchors_conflict_url_words(self, anchor: str):
        # 检查是否已经插入过该条记录
        select_query = f'''SELECT id, url, anchor, words FROM news_pages.anchors_conflict_url_words where anchor=%s'''
        result = self.__execute_query__(select_query, (anchor,), True, False)
        return result

    def update_anchors_conflict_url_words(self, id: int, conflict_words: str, checked_time: datetime):
        # 检查是否已经插入过该条记录
        select_query = f'''update news_pages.anchors_conflict_url_words set anchors_conflict_url_words.words=%s,checked_time=%s where id=%s'''
        self.__execute_query__(select_query, (conflict_words, checked_time, id), False, False)

    def del_anchors_conflict_url_words_row(self, row_id: int):
        # 检查是否已经插入过该条记录
        select_query = f'''delete from news_pages.anchors_conflict_url_words where id=%s'''
        self.__execute_query__(select_query, (row_id,), False, False)

    def drop_anchors_conflict_url_words_table(self):
        drop_query = f'''drop table if exists news_pages.anchors_conflict_url_words'''
        self.__execute_query__(drop_query, (), False, False)

    def create_anchors_conflict_url_words_table(self):
        create_query = f'''create table news_pages.anchors_conflict_url_words(
        id int auto_increment primary key not null,
        url tinytext not null ,
        anchor tinytext not null ,
        words text not null ,
        checked_time datetime not null 
        )'''
        self.__execute_query__(create_query, (), False, False)

    def create_article_content_table(self):
        create_query = f'''create table news_pages.article_content
(
    id         int auto_increment primary key not null,
    url        tinytext                       not null,
    parent_url tinytext                       not null,
    content    text                           not null
)'''
        self.__execute_query__(create_query, (), False, False)

    def create_pages_source_code(self):
        create_query = f'''create table news_pages.pages_source_code
(
    id           int auto_increment primary key not null,
    url          text                           not null,
    parent_url   text                           not null,
    source_code  mediumtext                     not null,
    crawled_time time                           not null
);'''
        self.__execute_query__(create_query, (), False, False)

    def create_article_urls(self):
        create_query = f'''create table news_pages.article_urls
(
    id           int auto_increment primary key not null,
    url          text                           not null,
    parent_url   text                           not null,
    crawled_time time                           not null
);'''
        self.__execute_query__(create_query, (), False, False)

    def create_tdk_table(self, database_name='tdks'):
        create_query = f'''create table tdks.tdk(
        id  int auto_increment primary key not null,
        language_code text not null,
        base_url text not null,
        url text not null,
        title text not null,
        description text not null,
        keywords text not null
        )
        '''
        self.__execute_query__(create_query, (), False, False, database=database_name)

    def save_tdk_table(self,
                       language_code: str,
                       base_url: str,
                       url: str,
                       title: str,
                       description: str,
                       keywords: str,
                       database_name='tdks'):
        save_query = f'''insert into tdks.tdk(language_code,
         base_url, url, title, description, keywords) 
         VALUES (%s,%s,%s,%s,%s,%s)
        '''
        self.__execute_query__(save_query,
                               (language_code,
                                base_url,
                                url,
                                title,
                                description,
                                keywords),
                               False,
                               False,
                               database=database_name)

    def read_tdk_table(self):
        read_query = f'''SELECT * FROM tdks.tdk'''

        return self.__execute_query__(read_query, (), True, False)

    def drop_article_content_table(self):
        drop_query = f'''drop table if exists news_pages.article_content'''
        self.__execute_query__(drop_query, (), False, False)

    def drop_article_urls(self):
        drop_query = f'''drop table if exists news_pages.article_urls'''
        self.__execute_query__(drop_query, (), False, False)

    def drop_pages_source_code(self):
        drop_query = f'''drop table if exists news_pages.pages_source_code'''
        self.__execute_query__(drop_query, (), False, False)

    def exporting_to_excel(self, datas: List):
        # datas = [{
        #     'Index': result[0],
        #     'Year&month': result[1],
        #     'URL': result[2],
        #     'Links': result[3],
        #     'Index Status': 'Indexed' if result[4] else 'Not Indexed',
        #     'Language': result[5],
        #     'Checked Time': result[6],
        #     'Agency': result[7],
        #     'Name': result[8],
        #     'Note': result[9]
        # },{
        #     'Index': result[0],
        #     'Year&month': result[1],
        #     'URL': result[2],
        #     'Links': result[3],
        #     'Index Status': 'Indexed' if result[4] else 'Not Indexed',
        #     'Language': result[5],
        #     'Checked Time': result[6],
        #     'Agency': result[7],
        #     'Name': result[8],
        #     'Note': result[9]
        # },]
        df = json_normalize(datas)
        df.to_excel(os.path.dirname(__file__) + '/find_anchors.xlsx', sheet_name='Sheet1', index=False)
        print("导出excel成功")
