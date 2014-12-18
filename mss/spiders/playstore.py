from urlparse import urljoin

from scrapy import Spider, Item, Field
from scrapy.http import Request, FormRequest
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, Join

from mss.utils import get_extracted


class PlayStoreItems(Item):
	app_id = Field(
		output_processor=TakeFirst()
	)
	name = Field(
		output_processor=TakeFirst()
	)
	category = Field(
		output_processor=TakeFirst()
	)
	category_url = Field(
		output_processor=TakeFirst()
	)
	price = Field(
		input_processor=Compose(
			lambda text: [line.strip().replace(" Buy", "").replace("Install", "Free") for line in text]
		),
		output_processor=TakeFirst()
	)
	offers_in_app_purchases = Field(
		output_processor=TakeFirst()
	)
	stars_count = Field(
		input_processor=Compose(lambda text: [line.strip().strip("()") for line in text]),
		output_processor=Join('')
	)
	video = Field(
		output_processor=TakeFirst()
	)
	screenshots = Field()
	description = Field(
		input_processor=Compose(lambda text: [line.strip() for line in text]),
	)
	update_date = Field(
		output_processor=TakeFirst()
	)
	file_size = Field(
		input_processor=Compose(lambda text: [line.strip() for line in text]),
		output_processor=TakeFirst()
	)
	installs = Field(
		input_processor=Compose(lambda text: [line.strip() for line in text]),
		output_processor=TakeFirst()
	)
	current_version = Field(
		input_processor=Compose(lambda text: [line.strip() for line in text]),
		output_processor=TakeFirst()
	)
	requires_android = Field(
		input_processor=Compose(lambda text: [line.strip() for line in text]),
		output_processor=TakeFirst()
	)
	offered_by = Field(
		output_processor=TakeFirst()
	)
	offered_by_url = Field(
		output_processor=TakeFirst()
	)

class PlayStore(Spider):
	name = "ps"
	start_urls = ["https://play.google.com/store?lang=eng"]

	download_delay = 0.5

	def parse(self, response):
		ul = response.css('.action-bar > .action-bar-item:first-child .dropdown-submenu > ul')
		urls = ul.xpath('li[1]//a/@href | li[2]//li[1]/a/@href').extract()
		for url in urls:
			yield Request(urljoin(response.url, url),
							callback=self.get_subcategories)

	def get_subcategories(self, response):
		menu_items = response.css('.action-bar > .action-bar-item')
		if len(menu_items) > 1:
			urls = get_extracted(menu_items, 1).css('ul.submenu-item-wrapper a::attr(href)').extract()
			for url in urls:
				yield Request(urljoin(response.url, url),
								callback=self.get_subcategories)
		else:
			urls = response.css('.cluster-heading > .title-link::attr(href)').extract()
			for url in urls:
				yield Request(urljoin(response.url, url),
								callback=self.get_apps)

	start = 0
	apps_urls = []
	def get_apps(self, response):
		cards = response.css('.card')
		if len(cards) > 0:
			self.apps_urls += cards.xpath('div/a/@href').extract()
			self.start += 60
			yield FormRequest(response.url,
								formdata={
									"start": str(self.start),
									"num": "60",
									"numChildren": "0",
									"ipf": "1",
									"xhr": "1"
								}, callback=self.get_apps)
		else:
			urls = self.apps_urls
			for url in urls:
				yield Request(urljoin(response.url, url),
								callback=self.get_app)

	def get_app(self, response):
		il = ItemLoader(item=PlayStoreItems(), response=response)
		il.add_css('app_id', '.details-wrapper::attr(data-docid)')
		il.add_css('name', '.document-title div::text')
		il.add_css('category', '.category span::text')
		il.add_css('category_url', '.category::attr(href)',
					Compose(lambda urls: [urljoin(response.url, url) for url in urls]))
		il.add_css('price', '.details-actions .price span::text')
		il.add_css('offers_in_app_purchases', '.inapp-msg::text')
		il.add_css('stars_count', '.stars-count::text')
		il.add_css('video', '.details-trailer > span::attr(data-video-url)')
		il.add_css('screenshots', '.screenshot::attr(src)')
		il.add_xpath('description', '//div[contains(@class, "show-more-content")]/div//text()')
		il.add_css('update_date', '[itemprop="datePublished"]::text')
		il.add_css('file_size', '[itemprop="fileSize"]::text')
		il.add_css('installs', '[itemprop="numDownloads"]::text')
		il.add_css('current_version', '[itemprop="softwareVersion"]::text')
		il.add_css('requires_android', '[itemprop="operatingSystems"]::text')
		il.add_css('offered_by', '[itemprop="author"] > a span::text')
		il.add_css('offered_by_url', '[itemprop="author"] > a::attr(href)',
					Compose(lambda urls: [urljoin(response.url, url) for url in urls]))
		yield il.load_item()
