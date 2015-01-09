import re

from scrapy.http import Request

from ebay import Ebay


class EbayDeals(Ebay):
    name = "EbayDeals"
    start_urls = ["http://deals.ebay.com/"]

    def parse(self, response):
        for block in response.css('.dd-dbc'):
            category = [h.strip() for h in block.css('h2::text').extract() if h.strip()]
            item_urls = block.css('.container:not(.dd-card-more) > a::attr(href)').extract()
            if block.css('.dd-card-more'):
                module_id = "".join(block.css('.dd-card-more a::attr(onclick)').extract())
                module_id = "".join(re.findall(r'\((\d+)\)', module_id))
                yield Request("http://deals.ebay.com/category/?moduleId=%s&debug=3&mredirect&cc=daily" % module_id,
                                callback=self.parse_item_urls,
                                meta={
                                    'category': category,
                                    'item_urls': item_urls
                                })
            else:
                for url in item_urls:
                    yield Request(url,
                                    callback=self.parse_item,
                                    meta={
                                        'category': category
                                    })

    def parse_item_urls(self, response):
        category = response.meta['category']
        item_urls = response.meta['item_urls']
        item_urls += response.css('.container:not(.dd-card-less) > a::attr(href)').extract()
        for url in item_urls:
            yield Request(url,
                            callback=self.parse_item,
                            meta={
                                'category': category
                            })
