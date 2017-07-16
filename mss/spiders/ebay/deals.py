'''MSS: Ebay Deals Spider'''
from scrapy import Request

from mss.spiders.ebay import BaseSpider


class DealsSpider(BaseSpider):
    '''MSS: Ebay Deals Spider'''
    name = 'EbayDeals'
    start_urls = [
        'http://www.ebay.com/deals/',
    ]

    def parse(self, response):
        # Spotlight Deal.
        hrefs = response.xpath('//div[h2[contains(., "Spotlight Deal")]]//a/@href')
        # Trending deals.
        hrefs += response.xpath('//div[h2[contains(., "Trending Deals")]]'
                                '/div/ul/li/div/a/@href')
        # Featured Deals.
        hrefs += response.css('.ebayui-dne-item-featured-card .col a::attr(href)')
        # Other deals.
        hrefs += response.css('.dne-pattern-title') \
                         .xpath('following-sibling::div[1]') \
                         .css('.item a[itemprop="url"]::attr(href)')
        for href in hrefs.extract():
            yield Request(
                response.urljoin(href),
                callback=self.parse_item,
            )
