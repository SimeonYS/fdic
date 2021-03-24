import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FdicItem
from itemloaders.processors import TakeFirst
import datetime
pattern = r'(\xa0)?'

class FdicSpider(scrapy.Spider):
	name = 'fdic'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [f'https://www.fdic.gov/news/press-releases/{year}/']

	def parse(self, response):
		post_links = response.xpath('//span[@class="title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.fdic.gov/news/press-releases/{self.year}/'
		if self.year >= 2017:
			self.year -= 1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="date"]/text()').get().split()[2]
		if not date:
			date = response.xpath('//span[@class="prdate"]/text()').get()
			date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@class="order-2 desktop:order-3 margin-x-2 desktop:margin-x-0 desktop:grid-col-9"]//text() | //div[@id="content"]//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FdicItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
