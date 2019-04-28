
BOT_NAME = 'Comparazer'

SPIDER_MODULES = ['Comparazer.spiders']
NEWSPIDER_MODULE = 'Comparazer.spiders'

USER_AGENT = 'Comparazer (http://example.com)'
# Obeying rules that sites set for bots
ROBOTSTXT_OBEY = True

# A bunch of parameters to optimize broad crawl
DEPTH_LIMIT=10
DEPTH_PRIORITY=1
CONCURRENT_REQUESTS = 100
REACTOR_THREADPOOL_MAXSIZE = 20
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 15
AJAXCRAWL_ENABLED = True

# File Export parameters
FEED_URI="file:///C:/Users/navi/Dropbox/Development/Scrappy/Comparazer/%(name)s.csv"
FEED_FORMAT="csv"
FEED_EXPORT_ENCODING="utf-8"

# Pipeline
ITEM_PIPELINES = {
    'Comparazer.pipelines.ComparazerPipeline': 300,
}
