'''MSS: Google Play Store Spider'''
import re

from dateutil import parser
from scrapy import Request, Spider

from mss.utils.strings import process_string


class PlayStoreSpider(Spider):
    '''MSS: Google Play Store Spider'''
    name = 'GooglePlayStore'
    start_urls = ['https://play.google.com/store/apps']

    def parse(self, response):
        '''Parse all categories apps'''
        hrefs = response.css('.child-submenu-link::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_category,
            )

    def parse_category(self, response):
        '''Parse specific category apps'''
        hrefs = response.css('.single-title-link > a::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_apps,
            )

    def parse_apps(self, response):
        '''Parse a list of apps'''
        hrefs = response.css('a[class="title"]::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_app,
            )

    def parse_app(self, response):
        '''Parse specific app details'''
        identifier = re.findall(r'id=(.+)', response.url)[0]
        title = response.css('.id-app-title::text').extract()[0]
        links = response.css('div[itemprop="author"] a')
        categories = []
        for link in links[1:]:
            name = link.xpath('string(span)').extract()[0]
            url = link.xpath('@href').extract()[0]
            categories.append({
                'name': process_string(name),
                'url': response.urljoin(url),
            })
        developer_name = links[0].xpath('string(span)').extract()[0]
        developer_url = links[0].xpath('@href').extract()[0]
        developer_links = response.css('.dev-link::attr(href)')
        developer_email = developer_links.re(r'mailto:(.+)')
        developer_website = developer_links.re(r'q=(.+)')
        rating = response.css('.score').xpath('@aria-label|text()').extract()
        last_updated = response.css('[itemprop="datePublished"]::text').extract()
        requirement = response.css('[itemprop="operatingSystems"]::text').extract()
        version = response.css('[itemprop="softwareVersion"]::text').extract()
        installs = response.css('[itemprop="numDownloads"]::text').extract()
        lines = response.css('.show-more-content div::text').extract()
        lines = [process_string(line) for line in lines]
        screenshots = response.css('.full-screenshot::attr(src)').extract()
        screenshots = [response.urljoin(screenshot) for screenshot in screenshots]
        cover = response.css('.cover-image::attr(src)').extract()[0]
        return {
            'identifier': identifier,
            'title': process_string(title),
            'description': '\n'.join(lines),
            'categories': categories,
            'cover': response.urljoin(cover),
            'screenshots': screenshots,
            'version': process_string((version or [''])[0]),
            'requirement': process_string((requirement or [''])[0]),
            'last_updated': (parser.parse(process_string(last_updated[0]))
                             if last_updated else ''),
            'installs': process_string((installs or [''])[0]),
            'rating': {
                'note': process_string(rating[0]),
                'count': float(rating[1]),
            } if rating else {},
            'developer': {
                'email': (developer_email or [''])[0],
                'name': process_string(developer_name),
                'website': (developer_website or[''])[0],
                'url': response.urljoin(developer_url),
            },
            'source': response.url,
        }
