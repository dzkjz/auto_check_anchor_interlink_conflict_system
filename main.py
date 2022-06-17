from news_page_crawler import crawler

c = crawler()
# c.continuous_start(headless=True)

c.pull_source_code()
