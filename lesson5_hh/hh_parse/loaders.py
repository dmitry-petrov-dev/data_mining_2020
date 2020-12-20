from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import HhJobParseItem
from .items import HhCompanyParseItem


def skills_out(data):
    return data


class HeadHunterJobLoader(ItemLoader):
    default_item_class = HhJobParseItem
    url_out = TakeFirst()
    name_out = TakeFirst()
    salary_in = "".join
    salary_out = TakeFirst()
    description_in = "".join
    description_out = TakeFirst()
    skills_out = skills_out
    company_url = TakeFirst()


class HeadHunterCompanyLoader(ItemLoader):
    default_item_class = HhCompanyParseItem
    url_out = TakeFirst()
    company_out = TakeFirst()
    company_url_out = TakeFirst()
    company_areas_out = TakeFirst()
    company_description_in = "".join
    company_description_out = TakeFirst()
