import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson4_scrapy.gb_parse.spiders.autoyoula import AutoyoulaSpider
from lesson4_scrapy.gb_parse.spiders.instagram import InstagramSpider


dotenv.load_dotenv('.env')
if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')

    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'), tag_list=['python'])
    crawl_proc.start()