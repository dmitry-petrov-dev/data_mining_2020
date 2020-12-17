import scrapy
import json
import datetime as dt
from ..loaders import InstagramLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32',
    }

    def __init__(self, login, password, tag_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.tag_list = tag_list
        super().__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tag_list:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)

    def tag_parse(self, response):
        tag_data = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        loader = InstagramLoader(response=response)
        loader.add_value('date_parse', dt.datetime.utcnow())
        loader.add_value('data', {
            'id': tag_data['id'],
            'name': tag_data['name'],
            'allow_following': tag_data['allow_following'],
            'is_following': tag_data['is_following'],
            'is_top_media_only': tag_data['is_top_media_only'],
            'profile_pic_url': tag_data['profile_pic_url'],
        })
        yield loader.load_item()
        yield from self.page_parse(tag_data, response)

    def page_parse(self, tag_data, response):
        if tag_data['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag_data['name'],
                'first': 100,
                'after': tag_data['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            yield response.follow(
                f'/graphql/query/?query_hash={self.query_hash["tag_paginate"]}&variables={json.dumps(variables)}',
                callback=self.page_parse)

        loader = InstagramLoader(response=response)
        loader.add_value('date_parse', dt.datetime.utcnow())
        for node in tag_data['edge_hashtag_to_media']['edges']:
            loader.add_value('data', node['node'])
            yield loader.load_item()

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])
