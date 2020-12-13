import scrapy
from ..loaders import HeadHunterJobLoader
from ..loaders import HeadHunterCompanyLoader


class HeadhunterSpider(scrapy.Spider):
    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    pag_template = {
        'pagination': '//div[contains(@data-qa, "pager-block")]//a[contains(@data-qa, "pager-page")]/@href',
        'job_url': '//div[contains(@data-qa, "vacancy-serp__vacancy")]//a[contains(@data-qa, "vacancy-serp__vacancy-title")]/@href'
    }
    job_template = {
        'name': '//h1[contains(@data-qa, "vacancy-title")]/text()',
        'salary': '//p[contains(@class, "vacancy-salary")]//text()',
        'description': '//div[contains(@class, "vacancy-section")]//text()',
        'skills': '//div[contains(@class,"bloko-tag-list")]//div[contains(@data-qa, "skills-element")]//text()',
        'company_url': '//a[contains(@data-qa, "vacancy-company-name")]/@href',
    }
    company_template = {
        'company': '//span[contains(@data-qa, "company-header-title-name")]/text()',
        'company_url': '//a[contains(@data-qa, "sidebar-company-site")]/@href',
        'company_areas': '//div[@class="employer-sidebar-block"][last()]/p/text()',
        'company_description': '//div[contains(@data-qa, "company-description-text")]//text()',
    }


    def parse(self, response):
        for pag_page in response.xpath(self.pag_template['pagination']):
            yield response.follow(pag_page, callback=self.parse)

        for job_page in response.xpath(self.pag_template['job_url']):
            yield response.follow(job_page, callback=self.job_parse)

    def job_parse(self, response):
        loader = HeadHunterJobLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.job_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()
        yield response.follow(response.xpath(self.job_template['company_url']).get(), callback=self.company_parse)

    def company_parse(self, response):
        loader = HeadHunterCompanyLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.company_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()