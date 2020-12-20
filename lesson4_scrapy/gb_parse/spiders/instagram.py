import scrapy
import json
import datetime as dt
from ..loaders import InstagramLoader
from ..items import InstagramItem, InstagramUser, InstagramFollowedUser, InstagramFollowUser


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    query_hash = {
        'url': '/graphql/query/?query_hash=',
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32',
        'followed_by': 'c76146de99bb02f6415203be841dd25a',
        'follow': 'd04b0a864b4b54837c0d870b0e77e076',
    }

    def __init__(self, login, password, tag_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.tag_list = tag_list
        self.users = ['guguquilombola', ]
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
                # for tag in self.tag_list:
                #   yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_parse)

    def user_parse(self, response):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield InstagramUser(
            date_parse=dt.datetime.utcnow(),
            data=user_data)
        yield from self.followers_parse(user_data, response)

    def followers_parse(self, user_data, response):
        variables = {
            'id': user_data['id'],
            'include_reel': 'true',
            'fetch_mutual': 'true',
            'first': 100,
        }
        yield response.follow(
            f'{self.query_hash["url"]}{self.query_hash["followed_by"]}&variables={json.dumps(variables)}',
            callback=self.followed_by_users_parse, cb_kwargs={'user_data': user_data})
        yield response.follow(
            f'{self.query_hash["url"]}{self.query_hash["follow"]}&variables={json.dumps(variables)}',
            callback=self.follow_users_parse, cb_kwargs={'user_data': user_data})

    def followed_by_users_parse(self, response, user_data):
        data = response.json()
        yield from self.get_followed_user_data(user_data, data['data']['user']['edge_followed_by']['edges'])
        if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            variables = {
                'id': user_data['id'],
                'include_reel': 'true',
                'fetch_mutual': 'true',
                'first': 100,
                'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor']
            }
            yield response.follow(
                f'{self.query_hash["url"]}{self.query_hash["followed_by"]}&variables={json.dumps(variables)}',
                callback=self.followed_by_users_parse, cb_kwargs={'user_data': user_data})

    def get_followed_user_data(self, user_data, followed_users):
        for user in followed_users:
            yield InstagramFollowedUser(
                user_id=user_data['id'],
                username=user_data['username'],
                followed_user_id=user['node']['id'],
                followed_users=user['node']['username'],
            )
            yield InstagramUser(
                date_parse=dt.datetime.utcnow(),
                data=user['node'])

    def follow_users_parse(self, response, user_data):
        data = response.json()
        yield from self.get_follow_user_data(user_data, data['data']['user']['edge_follow']['edges'])
        if data['data']['user']['edge_follow']['page_info']['has_next_page']:
            variables = {
                'id': user_data['id'],
                'include_reel': 'true',
                'fetch_mutual': 'true',
                'first': 100,
                'after': data['data']['user']['edge_follow']['page_info']['end_cursor']
            }
            yield response.follow(
                f'{self.query_hash["url"]}{self.query_hash["follow"]}&variables={json.dumps(variables)}',
                callback=self.follow_users_parse, cb_kwargs={'user_data': user_data})

    def get_follow_user_data(self, user_data, follow_users):
        for user in follow_users:
            yield InstagramFollowUser(
                user_id=user_data['id'],
                username=user_data['username'],
                follow_user_id=user['node']['id'],
                follow_users=user['node']['username'],
            )
            yield InstagramUser(
                date_parse=dt.datetime.utcnow(),
                data=user['node'])

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
