'''MSS: Ebay Products Spider'''
from scrapy import Request

from mss.spiders.ebay import BaseSpider


class ProductsSpider(BaseSpider):
    '''MSS: Ebay Products Spider'''
    name = 'EbayProducts'
    start_urls = [
        'https://www.ebay.com/sch/i.html?_nkw=all+categories&_sac=1#seeAllAnchorLink',
    ]

    def parse(self, response):
        '''Parse a list of all categories'''
        hrefs = response.css('#LeftNavCategoryContainer .cat-link a::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_category,
            )

    def parse_category(self, response):
        '''Parse specific category items'''
        hrefs = response.css('#ListViewInner a[title]::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_item,
            )
        next_page = response.css('#Pagination a.next::attr(href)').extract()
        if next_page:
            yield Request(
                response.urljoin(next_page[0]),
                callback=self.parse_category,
            )
