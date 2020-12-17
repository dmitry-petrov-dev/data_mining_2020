# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['gb_parse_11_2']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item


class GbImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.get('data')[0].get('profile_pic_url'):
            yield Request(item.get('data')[0].get('profile_pic_url'))
        if item.get('data')[0].get('thumbnail_src'):
            yield Request(item.get('data')[0].get('thumbnail_src'))

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        return item
