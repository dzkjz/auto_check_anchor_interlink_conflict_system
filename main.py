from news_page_crawler import crawler
import check_anchors

c = crawler()
# 抓取news详情页URL
c.continuous_start(headless=True)
# 抓取news下详情页面源码
c.pull_source_code()

# 提取详情页内容文本
check_anchors.start(no_save_to_database=False)

# 分析冲突细节
check_anchors.conflict_filter(no_save_to_database=False)
