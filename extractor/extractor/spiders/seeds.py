import re

import scrapy
from scrapy.utils.url import parse_url

from ..items import ProductItem


class BoiteAGrainesSpider(scrapy.Spider):
    name = 'boiteagraines'
    start_urls = [
        'https://laboiteagraines.com/categorie-produit/2-graines-semences-graine-semence-potageres-legumes/15-graines-legumes-feuille/',
        'https://laboiteagraines.com/categorie-produit/2-graines-semences-graine-semence-potageres-legumes/',
        'https://laboiteagraines.com/categorie-produit/13-graines-semences-fleurs/',
        'https://laboiteagraines.com/categorie-produit/72-graines-semences-plantes-aromatiques/',
        'https://laboiteagraines.com/categorie-produit/uncategorized/',
        'https://laboiteagraines.com/categorie-produit/4-graines-semences-plantes-rares/',
    ]

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css('.product-details > a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        next_page_url = response.css('.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_product(self, response):
        """Analysis of the product page."""
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
        """Process the downloaded response."""
        product_urls = response.css('.product__title > a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        next_page_url = response.css('.pagination__item--next a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
        
    def parse_product(self, response):
        """Analysis of the product page."""
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
        """Process the downloaded response."""
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
        """Analysis of the product page."""
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

    
class FermedemaintemartheSpider(scrapy.Spider):
    name = 'fermedesaintmarthe'
    start_urls = [
        'https://www.fermedesaintemarthe.com/CT-3146-graines-potageres.aspx',
        'https://www.fermedesaintemarthe.com/CT-3172-graines-d-aromatiques-et-medicinales.aspx',
        'https://www.fermedesaintemarthe.com/CT-2001-graines-de-fleurs.aspx',
        'https://www.fermedesaintemarthe.com/CT-3194-pommes-de-terre.aspx',
    ]

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css('.item .name a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        next_page_url = response.css('.LinkNext a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('.pageTitle span::text').get()
        item['available'] = not response.css('.dispo')
        item['promotion'] = not not response.css('.old')
        if item['promotion']:
            item['old_price'] = response.css('.old .amount::text').get()

        item['price'] = response.css('.new .amount::text').get()
        # Un tableau
        item['raw_string'] = response.css('.featureTable tr td::text').getall()
                    
        return item


class ComptoirdesgrainesSpider(scrapy.Spider):
    # TODO: availability
    name = 'comptoirdesgraines'
    start_urls = ['https://www.comptoir-des-graines.fr/fr/']

    def parse(self, response):
        """Process the downloaded response.""" 
        # links in the navbar
        categories = response.css('.sub a::attr(href)').getall()
        for categorie in categories:
            yield scrapy.Request(response.urljoin(categorie))
        
        next_page_url = response.css('.pagination_next a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
            
        product_urls = response.css('.product-name::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        
        data = response.css('script[type~="application/ld+json"]::text').get()
        # Removes indent
        data = re.sub(r'[\n\t]', '', data)
        data = eval(data)
        
        item['product_name'] = data['name']
        item['price'] = data['offers']['price']
        item['currency'] = data['offers']['priceCurrency']
        item['product_id'] = data['productID']
        
        # seed number
        item['raw_string'] = response.css('.seed-number::text').get().strip()

        return item


class GrainesdefolieSpider(scrapy.Spider):
    # not working
    name = 'grainesdefolie'
    start_urls = [
        'https://www.grainesdefolie.com/102-exotiques',
        'https://www.grainesdefolie.com/101-fleurs-fruits',
        'https://www.grainesdefolie.com/67-aromates',
        'https://www.grainesdefolie.com/39-potager',
        'https://www.grainesdefolie.com/100-graines-bio',
    ]

    def parse(self, response):
        """Process the downloaded response."""
        pattern = r'ajax_token\s*=\s*"([^"]+)'
        token = re.search(pattern, response.text).group(1)
        formdata = {
            'token': token,
            'controller': 'product',
            'id_customization': '0',
            'qty': '1'
        }

        next_page_url = response.css('.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
     
        quantities = {}
        product_ids = response.css('.productattributelist::attr(data-id)').getall()
        for product_id in product_ids:
            values = response.css(f'.productattributelist[data-id~="{product_id}"] option::attr(value)').getall()
            quantities[product_id] = values
        
        """
        product_urls = response.css('.product-title a::attr(href)').getall()
        for product_url in product_urls:
            match = re.search(r'(\d+)-\d+', product_url)
            if not match:
                continue"""

            #id_product = match.group(1)
            #formdata['id_product'] = id_product
        for id_product in quantities.keys():
            for quantity in quantities[id_product]:
                formdata['group[5]'] = quantity

                # TODO: erreur 302
                yield scrapy.FormRequest(
                    'https://www.grainesdefolie.com/index.php',
                    self.parse_product,
                    method='POST',
                    formdata=formdata
                )

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('span[itemprop~=price]::attr(content)').get()

        return item


class SanRivalSpider(scrapy.Spider):
    name = 'sanrival'
    start_urls = [
        'https://sanrivaljardin.com/19-aromatiques',
        'https://sanrivaljardin.com/10-graines-potageres',
        'https://sanrivaljardin.com/11-graines-de-fleurs',
        'https://sanrivaljardin.com/87-gamme-bio',
        'https://sanrivaljardin.com/12-gamme-premium',
        'https://sanrivaljardin.com/17-gamme-kids',

    ]

    def parse(self, response):
        """Process the downloaded response."""
        # single page
        product_urls = response.css('.product-title > a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)
        categorie_urls = response.css('.elementor-button ::attr(href)').getall()
        for categorie_url in categorie_urls:
            yield scrapy.Request(response.urljoin(categorie_url))

    def parse_product(self, response):
        """Analysis of the product page."""
        # messy data
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('.current-price span::attr(content)').get()
        
        # sometimes quantity and/or seed number
        item['raw_string'] = ' '.join(response.css('.product-information span::text').getall())

        return item


class FabreSpider(scrapy.Spider):
    # not working
    name = 'fabre'
    start_urls = [
        'https://www.fabre-graines.com/fr/graines-potageres.html',
        'https://www.fabre-graines.com/fr/graines-de-fleurs.html',
        'https://www.fabre-graines.com/fr/semences-fourrageres-graminees-1.html',
        'https://www.fabre-graines.com/fr/semences-fourrageres-legumineuses-1.html'
    ]

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css('article a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)

        
class GrainesdelPaisSpider(scrapy.Spider):
    name = 'grainesdelpais'
    start_urls = ['https://www.grainesdelpais.com/catalogue_en_ligne_2.php']

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css('.lienfiche::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)

        categorie_urls = response.css('.fichecontdossier a::attr(href)').getall()
        for categorie_url in categorie_urls:
            yield scrapy.Request(response.urljoin(categorie_url))

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['description'] = response.css('.partiesouligne p::text').get()
        # densité possible

        # sous la forme `0.8 g - 3.40 €`
        item['raw_string'] = response.css('.prixsachet::text').get()
        item['price'] = -1

        return item


class GrainesBaumauxSpider(scrapy.Spider):
    name = 'grainesbaumaux'
    start_urls = [
        'https://www.graines-baumaux.fr/168712-semences-potageres',
        'https://www.graines-baumaux.fr/168637-graines-fourrageres-et-engrais-verts',
        'https://www.graines-baumaux.fr/167226-semences-aromatiques-et-officinales',
        'https://www.graines-baumaux.fr/167553-semences-florales'
    ]

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css('.product-title a::attr(href)').getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)

        categorie_urls = response.css('.subcategory-link::attr(href)').getall()
        for categorie_url in categorie_urls:
            yield scrapy.Request(response.urljoin(categorie_url))

        next_page_url = response.css('.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('.current-price span::attr(content)').get()
        item['available'] = not not response.css('span.font-extra .product-available').get()
        item['promotion'] = not not response.css('.product-discount').getall()

        # weight e.g. : « 0,25 g. NT »
        item['raw_string'] = response.css('div[itemprop~=description]::text').get()

        return item