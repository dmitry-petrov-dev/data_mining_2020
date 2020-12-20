# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AutoYoulaItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    autor = scrapy.Field()
    specification = scrapy.Field()
    phone = scrapy.Field()


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    images = scrapy.Field()


class InstagramUser(InstagramItem):
    user_id = scrapy.Field()
    username = scrapy.Field()


class InstagramFollowedUser(InstagramUser):
    followed_user_id = scrapy.Field()
    followed_users = scrapy.Field()


class InstagramFollowUser(InstagramUser):
    follow_user_id = scrapy.Field()
    follow_users = scrapy.Field()