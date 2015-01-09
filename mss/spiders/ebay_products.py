from scrapy.http import Request

from ebay import Ebay


class EbayProducts(Ebay):
    name = "Ebay"
    start_urls = ["http://www.ebay.com/sch/sch/allcategories/all-categories"]

    def parse(self, response):
        urls = [url.replace("chp", "sch") + "/i.html"
                    for url in response.css('.gcmc .gcma ul a::attr(href)').extract()
                        if "chp" in url]
        for url in urls:
            yield Request(url, callback=self.parse_items)

    def parse_items(self, response):
        item_urls = response.css('#ListViewInner li h3 a::attr(href)').extract()
        next_page = "".join(response.css('#Pagination a.next::attr(href)').extract())
        if next_page:
            yield Request(next_page, callback=self.parse_items)
        category = response.css('#cbelm .clt h1 .kwcat b::text').extract()
        for url in item_urls:
            yield Request(url,
                            callback=self.parse_item,
                            meta={
                                'category': category
                            })
