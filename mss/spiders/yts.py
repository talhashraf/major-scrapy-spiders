'''MSS: YTS Movies Spider'''
from scrapy import Request, Spider

from mss.utils.strings import process_string


class YTSMoviesSpider(Spider):
    '''MSS: YTS Movies Spider'''
    name = 'YTSMoviesSpider'
    start_urls = [
        'https://yts.ag/browse-movies',
    ]

    def parse(self, response):
        '''Parse a list of movies'''
        hrefs = response.css('.browse-movie-link::attr(href)').extract()
        for href in hrefs:
            yield Request(
                response.urljoin(href),
                callback=self.parse_movie,
            )
        next_page = response.xpath('//a[contains(text(), "Next")]/@href').extract()
        if next_page:
            yield Request(response.urljoin(next_page[0]))

    def parse_movie(self, response):
        '''Parse specific movie page'''
        info = response.css('#movie-info')
        name = info.css('h1::text').extract()[0]
        year, genres = info.css('h2::text').extract()
        likes = (info.css('#movie-likes::text').extract()[0] or [0])[0]
        ratings = info.css('.rating-row')
        imdb = ratings.xpath('span[@itemprop="ratingValue"]/text()').extract()[0]
        cover = response.css('#movie-poster img::attr(src)').extract()[0]
        synopsis = response.css('#synopsis p::text').extract()[0]
        synopsis = process_string(synopsis).strip('"')
        item = {
            'name': process_string(name),
            'synopsis': synopsis,
            'year': int(year),
            'genres': genres.split(' / '),
            'cover': response.urljoin(cover),
            'rating': {
                'likes': int(likes),
                'imdb': float(process_string(imdb)),
            },
            'download': {'links': []},
            'similar_movies': [],
            'screenshots': [],
            'directors': [],
            'actors': [],
        }
        # Add movie directors.
        rows = response.css('.directors .list-cast')
        for row in rows:
            link = row.xpath('div/a')
            name = link.css('span[itemprop="name"]::text').extract()[0]
            photo = link.xpath('img[not(contains(@src, "default_avatar"))]/@src').extract()
            url = link.xpath('@href').extract()[0]
            item['directors'].append({
                'name': process_string(name),
                'photo': response.urljoin(photo[0]) if photo else '',
                'url': response.urljoin(url)
            })
        # Add movie actors.
        rows = response.css('.actors .list-cast')
        for row in rows:
            link = row.xpath('div/a')
            name = link.css('span[itemprop="name"]::text').extract()[0]
            as_name = row.css('.list-cast-info::text').re('as (.+)')[0]
            photo = link.xpath('img[not(contains(@src, "default_avatar"))]/@src').extract()
            url = link.xpath('@href').extract()[0]
            item['actors'].append({
                'name': {
                    'original': process_string(name),
                    'appeared_as': process_string(as_name),
                },
                'photo': response.urljoin(photo[0]) if photo else '',
                'url': response.urljoin(url),
            })
        # Add ratings (critics and audience).
        ratings = info.css('.rating-row')
        for rating in ratings:
            rating = rating.xpath('span/text()').extract()
            if len(rating) == 2:
                key = rating[1].replace(' - ', '')
                item['rating'].update({
                    key: process_string(rating[0]),
                })
        # Add download links.
        links = info.xpath('p/a')
        for link in links:
            url = link.xpath('@href').extract()[0]
            quality = link.xpath('string()').extract()[0]
            item['download']['links'] = {
                'quality': process_string(quality),
                'url': response.urljoin(url),
            }
        # Add screenshots.
        links = response.css('.screenshot a')
        for link in links:
            url = link.xpath('@href').extract()[0]
            url = response.urljoin(url)
            if link.xpath('@id'):
                item['trailer'] = url
                continue
            item['screenshots'].append(url)
        # Add similar movies.
        links = response.css('#movie-related a')
        for link in links:
            title, year = link.xpath('@title').re(r'(.+) \((\d+)\)')
            url = link.xpath('@href').extract()[0]
            cover = link.xpath('img/@src').extract()[0]
            item['similar_movies'].append({
                'title': process_string(title),
                'year': int(year),
                'url': response.urljoin(url),
                'cover': response.urljoin(cover),
            })
        return item
