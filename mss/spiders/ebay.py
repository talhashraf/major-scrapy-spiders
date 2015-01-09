from scrapy import Spider, Item, Field


class EbayItems(Item):
    url = Field()
    title = Field()
    category = Field()
    sub_title = Field()
    current_price = Field()
    views_per_hour = Field()
    save_price = Field()
    watching = Field()

class Ebay(Spider):
    download_delay = 0.5

    def parse(self, response):
        pass

    def parse_item(self, response):
        item = EbayItems()
        item['url'] = response.url
        item['title'] = "".join(response.css('#itemTitle::text').extract())
        item['category'] = "".join(response.meta['category'])
        item['sub_title'] = "".join(response.css('#subTitle::text').extract()).strip()
        item['current_price'] = "".join(response.css('#prcIsum::text').extract())
        item['views_per_hour'] = "".join(response.css('#vi_notification_new span::text').extract())
        item['save_price'] = "".join(response.css('#youSaveSTP::text').extract()).replace(u"\xa0", " ").strip()
        item['watching'] = "".join(response.css('#vi-bybox-watchers *::text').extract()).strip()
        return item
