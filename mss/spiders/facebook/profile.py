'''MSS: Facebook Profile Spider'''
from dateutil import parser
from scrapy import Request

from mss.spiders.facebook.login import LoginSpider
from mss.utils.strings import process_string


class ProfileSpider(LoginSpider):
    '''MSS: Facebook Profile Spider'''
    name = 'FacebookProfileSpider'

    def parse_profile(self, response):
        '''Parse user profile page'''
        response = html_response(response, 'u_0_13')
        href = response.css('a[data-tab-key="about"]::attr(href)').extract()[0]
        return Request(
            response.urljoin(href),
            callback=self.parse_about,
        )

    def parse_about(self, response):
        '''Parse user profile about page'''
        notifications_count = response.xpath(
            'string(//span[@id="notificationsCountValue"])').extract()[0]
        # Extract profile information.
        response_ = html_response(response, 'u_0_13')
        name = response_.css('#fb-timeline-cover-name::text').extract()[0]
        picture = response_.css('.profilePic::attr(src)').extract()[0]
        cover = response_.css('.coverPhotoImg::attr(src)').extract()[0]
        item = {
            'name': process_string(name),
            'photo': response.urljoin(picture),
            'cover': response.urljoin(cover),
            'url': response.url,
            'phones': [],
            'emails': [],
            'notifications': {
                'count': int(notifications_count or 0),
            },
        }
        # Extract user `About`.
        response_ = html_response(response, 'u_0_2d')
        data_list = lambda name: response_.xpath('//span[div[contains(., "%s")][1]]/div' % name) \
                                          .xpath('string()').extract()[1:]
        item['address'] = '\n'.join(data_list('Address'))
        dob = data_list('Birthday')
        if dob:
            item['dob'] = parser.parse(process_string(dob[0]))
        for phone in data_list('Phones'):
            item['phones'].append(process_string(phone))
        for email in data_list('Email'):
            item['emails'].append(process_string(email))
        return item


def html_response(response, node_id):
    '''Return `response` replaced with HTML placed under code tag'''
    body = response.xpath('//code[@id="%s"]' % node_id).extract()[0]
    body = body.split('<!--')[1].split('-->')[0]
    return response.replace(body=body.strip())
