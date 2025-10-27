import scrapy


class TorobSpiderSpider(scrapy.Spider):
    name = "torob_spider"
    allowed_domains = ["torob.com"]
    start_urls = ["https://torob.com"]

    def parse(self, response):
        pass
