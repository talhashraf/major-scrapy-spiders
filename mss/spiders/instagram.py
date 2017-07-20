'''MSS: Instagram Spider'''
import json

from scrapy import Spider


class Instagram(Spider):
    '''MSS: Instagram Spider'''
    name = 'Instagram'
    start_urls = [
        'https://www.instagram.com/nike/',
    ]

    def parse(self, response):
        '''Parse profile JSON data'''
        json_string = response.xpath('//script/text()').re(r'sharedData = (.+);')[0]
        return json.loads(json_string)
