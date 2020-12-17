# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhJobParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()


class HhCompanyParseItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    company = scrapy.Field()
    company_url = scrapy.Field()
    company_areas = scrapy.Field()
    company_description = scrapy.Field()
