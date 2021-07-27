import scrapy
from scrapy.utils.url import parse_url

from ..items import ProductItem


class BoiteAGrainesSpider(scrapy.Spider):
    name = 'boite-a-graines'
    start_urls = [
        'https://laboiteagraines.com/categorie-produit/2-graines-semences-graine-semence-potageres-legumes/15-graines-legumes-feuille/',
        'https://laboiteagraines.com/categorie-produit/2-graines-semences-graine-semence-potageres-legumes/',
        'https://laboiteagraines.com/categorie-produit/13-graines-semences-fleurs/',
        'https://laboiteagraines.com/categorie-produit/72-graines-semences-plantes-aromatiques/',
        'https://laboiteagraines.com/categorie-produit/uncategorized/',
        'https://laboiteagraines.com/categorie-produit/4-graines-semences-plantes-rares/',
    ]

    def parse(self, response):
        product_urls = response.css('.product-details > a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        next_page_url = response.css('.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_product(self, response):
        """
        Analysis of the product page.
        """
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('.product_title::text').get()
        item['price'] = response.css('.product-information .price bdi::text').get()
        item['currency'] = 'EUR'
        item['description'] = response.css('.woocommerce-product-details__short-description p::text').get()

        item['published'] = response.css('meta[property~="article:published_time"]::attr(content)').get()  # '2016-03-25T11:15:56Z'
        item['last_modified'] = response.css('meta[property~="article:modified_time"]::attr(content)').get()
        return item


class KokopelliSpider(scrapy.Spider):
    # TODO: from sitemap
    # user-agent nécessaire
    name = 'kokopelli'
    start_urls = ['https://kokopelli-semences.fr/fr/c/semences']

    def parse(self, response):
        product_urls = response.css('.product__title > a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        next_page_url = response.css('.pagination__item--next a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
        
    def parse_product(self, response):
        """
        Analysis of the product page.
        """
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['promotion'] = any(x == "PROMOTION" for x in response.css('h3::text').getall())
        item['description'] = response.css('.product__description p::text').getall()
        item['raw_string'] = response.css('.product__informations li::text').getall()  # Array

        data = eval(response.css('script[type~="application/ld+json"]::text').get())
        item['product_name'] = data['name']
        item['product_id'] = data['productID']
        item['price'] = data['offers']['price']
        item['currency'] = data['offers']['priceCurrency']
        item['available'] = data['offers']['availability'].endswith('InStock')
        item['latin_name'] = data['alternateName']
        return item


class BiaugermeSpider(scrapy.Spider):
    name = 'biaugerme'
    start_urls = [
        'https://www.biaugerme.com/potageres',
        'https://www.biaugerme.com/fleurs/toutes-nos-fleurs',
        'https://www.biaugerme.com/aromatiques'
    ]

    def parse(self, response):
        product_urls = response.css('.lpPLink::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)

        variety_urls = response.css('.elementContent a::attr(href)').getall()
        for variety_url in variety_urls:
            yield scrapy.Request(response.urljoin(variety_url))

        # TODO: mêmes opérations que précédemment, seule la classe change
        variety_urls = response.css('.elementTitle a::attr(href)').getall()
        for variety_url in variety_urls:
            yield scrapy.Request(response.urljoin(variety_url))

    def parse_product(self, response):
        """
        Analysis of the product page.
        """
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['density'] = response.css('#description strong::text').get()
        item['available'] = not response.css('.msgSoldOut')


        for selector in response.css('.fpBktParam'):
            item['raw_string'] = selector.css('span::text').get()
            item['price'] = selector.css('div::text').getall()[1]
            yield item