from db_handler import database_handler
from news_page_crawler import crawler
import check_anchors




def initialize_database():
    dh = database_handler()
    dh.drop_article_urls()
    dh.create_article_urls()
    dh.drop_pages_source_code()
    dh.create_pages_source_code()
    dh.drop_article_content_table()
    dh.create_article_content_table()
    dh.drop_anchors_conflict_url_words_table()
    dh.create_anchors_conflict_url_words_table()


def recrawl_page_content():
    initialize_database()

    c = crawler()
    # 抓取news详情页URL
    c.continuous_start(headless=True, multingual=False)
    # 抓取news下详情页面源码
    c.pull_source_code()


# 是否需要重新爬网页
need_recrawl_page_content = False
if need_recrawl_page_content:
    recrawl_page_content()

# 是否需要重新解析源码到内容中
need_reparse_page_content = False
if need_reparse_page_content:
    check_anchors.source_parse_to_text()
# 提取详情页内容文本
print("提取详情页内容文本")
need_analysis_conflict = False
check_anchors.start(no_save_to_database=False, need_find_conflict=need_analysis_conflict)
