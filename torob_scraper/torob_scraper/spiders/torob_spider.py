# torob_scraper/spiders/torob_search.py
import scrapy
import urllib.parse
import json
import re

class TorobSearchSpider(scrapy.Spider):
    name = "torob_search"
    allowed_domains = ["torob.com"]

    def __init__(self, query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not query:
            raise ValueError("لطفاً نام محصول را با -a query=\"نام محصول\" بدهید")
        self.start_urls = [f"https://torob.com/search/?query={urllib.parse.quote(query)}"]

    def parse(self, response):
        first_product = response.css('a[href*="/p/"]::attr(href)').get()
        if not first_product:
            yield {"error": "محصولی یافت نشد"}
            return

        product_url = response.urljoin(first_product)
        yield scrapy.Request(product_url, callback=self.parse_product)

    def parse_product(self, response):
        item = {}

        item["name"] = response.css('.Showcase_name__hrttI h1::text').get(default="").strip()

        cheapest = {}
        seller_link = response.css('div.Showcase_cheapest_seller__TJpf9 a::attr(href)').get()
        if seller_link:
            cheapest["link"] = response.urljoin(seller_link)
            cheapest["shop"] = response.css('div.Showcase_buy_box_text__otYW_:first-child::text').get(default="").strip()
            price_text = response.css('div.Showcase_buy_box_text__otYW_:last-child::text').get(default="")
            cheapest["price_text"] = price_text.strip()

            price_match = re.search(r'[\d,]+', price_text.replace('٫', ''))
            if price_match:
                cheapest["price"] = int(price_match.group().replace(',', ''))
            else:
                cheapest["price"] = None
        else:
            cheapest = None

        item["cheapest"] = cheapest

        specs = {"key_specs": [], "general_specs": {}}

        key_specs = response.css('div.key_specs .key-specs-container')
        for spec in key_specs:
            title = spec.css('.keys-values span::text').get(default="").strip()
            value = spec.css('.keys-values:last-child::text').get(default="").strip()
            if title and value:
                specs["key_specs"].append({"title": title, "value": value})

        general_specs = response.css('div.sub-section .detail-title')
        for title_el in general_specs:
            title = title_el.css('::text').get(default="").strip()
            value_el = title_el.xpath('following-sibling::div[1]')
            value = value_el.css('::text').get(default="").strip()
            if title and value:
                specs["general_specs"][title] = value

        item["specs"] = specs

        yield item