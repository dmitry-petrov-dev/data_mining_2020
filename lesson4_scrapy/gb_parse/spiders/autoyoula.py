import re
import base64
import scrapy
import pymongo


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']

    css_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['gb_parse_11'][self.name]

    def parse(self, response):
        for brand in response.css(self.css_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.css_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.css_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,
            'autor': self.get_autor(response),
            'specification': self.get_specification(response),
            'phone': self.get_phone(response)
        }

        self.db.insert(data)

    def get_specification(self, response):
        spec_dict = {}
        for itm in response.css('div.AdvertSpecs_row__ljPcX'):
            spec_dict[itm.css('div.AdvertSpecs_label__2JHnS::text').get()] = itm.css(
                'div.AdvertSpecs_data__xK2Qx::text').get() or itm.css('a::text').get()
        return spec_dict

    def get_autor(self, response):
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None

    def get_phone(self, response):
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"phone%22%2C%22([0-9|a-zA-Z]+)%3D%3D%22%2C%22time")
        result = re.findall(re_str, script)
        return self.decode_phone(result[0])

    def decode_phone(self, b64_phone):
        b64_phone = base64.b64decode(b64_phone.encode("UTF-8") + b'=' * (-len(b64_phone) % 4))
        return base64.b64decode(b64_phone).decode('UTF-8')