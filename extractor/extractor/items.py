# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    url = scrapy.Field()
    vendor = scrapy.Field()
    latin_name = scrapy.Field()
    product_name = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()  # old price indicated during promotions
    currency = scrapy.Field()
    weight = scrapy.Field()  # in grams
    seed_number = scrapy.Field()
    description = scrapy.Field()
    published = scrapy.Field()
    last_modified = scrapy.Field()
    product_id = scrapy.Field()
    promotion = scrapy.Field()  # bool
    available = scrapy.Field()  # bool
    density = scrapy.Field()
    timestamp = scrapy.Field()

    raw_string = scrapy.Field()