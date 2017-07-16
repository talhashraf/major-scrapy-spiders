'''MSS: Ebay Base Spider Class'''
from scrapy import Spider
from scrapy.shell import inspect_response

from mss.utils.strings import process_string


class BaseSpider(Spider):
    '''MSS: Ebay Base Spider Class'''
    name = 'EbayBaseSpider'

    def parse(self, response):
        raise NotImplementedError

    def parse_item(self, response):
        '''Parse specific ebay item'''
        price = (response.css('#prcIsum::text').extract() or
                 response.css('#mm-saleDscPrc::text').extract())
        # Ignore item if current price is not found.
        if not price:
            return
        price_original = (response.css('#orgPrc::text').extract() or
                          response.css('#mm-saleOrgPrc::text').extract()) or ''
        if price_original:
            price_original = process_string(price_original[0])
        price_save = (response.css('#youSaveSTP::text').extract() or
                      response.css('#mm-saleAmtSavedPrc::text').extract()) or ''
        if price_save:
            price_save = process_string(price_save[0])
        title = response.css('#itemTitle::text').extract()[0]
        breadcrumb = response.css('#vi-VR-brumb-lnkLst ul')
        category = breadcrumb.xpath('li//text()').extract()[-1]
        breadcrumb = breadcrumb.xpath('string()').extract()[0]
        condition = response.css('#vi-itm-cond::text').extract()[0]
        watching = response.css('#vi-bybox-watchers span::text').extract()
        photo = response.css('#icImg::attr(src)').extract()
        item = {
            'url': response.url,
            'title': process_string(title),
            'condition': process_string(condition),
            'breadcrumb': process_string(breadcrumb),
            'photo': response.urljoin(photo[0]) if photo else '',
            'category': process_string(category),
            'price': {
                'original': price_original,
                'save': price_save,
                'current': process_string(price[0]),
            },
        }
        if watching:
            item['watching'] = process_string(watching[0])
        if not (price_original and price_save):
            item['price'] = item['price']['current']
        return item
