from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson5_hh.hh_parse.spiders.headhunter import HeadhunterSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('hh_parse.settings')

    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(HeadhunterSpider)
    crawl_proc.start()
