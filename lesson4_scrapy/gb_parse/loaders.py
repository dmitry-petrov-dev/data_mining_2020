import re
import base64
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoYoulaItem


def get_specification(itm):
    tag = Selector(text=itm)
    result = {
        tag.css('.AdvertSpecs_label__2JHnS::text').get(): tag.css('.AdvertSpecs_data__xK2Qx::text').get() or tag.css(
            'a::text').get()}
    return result



def get_autor(js_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, js_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


def get_phone(js_string):
    re_str = re.compile(r"phone%22%2C%22([0-9|a-zA-Z]+)%3D%3D%22%2C%22time")
    result = re.findall(re_str, js_string)
    return decode_phone(result[0])


def decode_phone(b64_phone):
    b64_phone = base64.b64decode(b64_phone.encode("UTF-8") + b'=' * (-len(b64_phone) % 4))
    return base64.b64decode(b64_phone).decode('UTF-8')


def specification_out(data: list):
    result = {}
    for itm in data:
        result.update(itm)
    return result


class AutoYoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_out = TakeFirst()
    autor_in = MapCompose(get_autor)
    autor_out = TakeFirst()
    specification_in = MapCompose(get_specification)
    specification_out = specification_out
    phone_in = MapCompose(get_phone)
    phone_out = TakeFirst()
