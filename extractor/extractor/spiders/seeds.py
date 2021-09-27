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

        # item['product_name'] = response.css('h1::text').get()
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

        next_page_url = response.css('.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
     
        quantities = {}
        product_ids = response.css('.productattributelist::attr(data-id)').getall()
        for product_id in product_ids:
            values = response.css(f'.productattributelist[data-id~="{product_id}"] option::attr(value)').getall()
            quantities[product_id] = values
        
        for id_product in quantities.keys():
            for quantity in quantities[id_product]:
                url = f'https://www.grainesdefolie.com/index.php?controller=product&token={token}&id_product={id_product}&id_customization=0&group[5]={quantity}&qty=1'
                yield scrapy.Request(url, self.parse_product, method='POST')

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        # Réécriture de l'url
        item['url'] = response.css('meta[property~="og:url"]::attr(content)').get()

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('span[itemprop~=price]::attr(content)').get()

        # quantity: « 100 graines * » OR « 5 grammes * »
        item['raw_string'] = response.css('#group_5 option[selected]::text').get()


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
        item['promotion'] = not not response.css('.product-discount').get()


        # weight e.g. : « 0,25 g. NT »
        item['raw_string'] = response.css('div[itemprop~=description]::text').get()

        return item

    
class PotageEtGourmandsSpider(scrapy.Spider):
    # very similar to `labanquedegraines.com`
    name = 'potageetgourmands'
    start_urls = ['https://potage-et-gourmands.fr/shop']

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css(
            '.product > a.woocommerce-loop-product__link::attr(href)'
        ).getall()
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

        item['product_name'] = response.css('h1::text').get()
        
        item['promotion'] = not not response.css('.summary .price del')
        if item['promotion']:
            item['old_price'] = response.css('.summary .price del .amount::text').get()
            item['price'] = response.css('.summary .price ins .amount::text').get()
        else:
            item['price'] = response.css('.summary .price .amount::text').get()

        item['available'] = not not response.css('.in-stock')
        # e.g. « 10 en stock »
        item['stock'] = response.css('.in-stock::text').get()

        # weight
        item['raw_string'] = response.css(
            '.woocommerce-product-details__short-description p::text'
        ).get()
        
        return item


class LaBanqueDeGrainesSpider(scrapy.Spider):
    # very similar to `potage-et-gourmands.fr`
    # les poids indiqués ne semblent pas fiables
    name = 'labanquedegraines'
    start_urls = ['https://labanquedegraines.com/categorie-produit/graines-potageres']

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css(
            '.woocommerce-loop-product__link::attr(href)'
        ).getall()
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

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('.summary .price bdi::text').get()

        item['available'] = not not response.css('.in-stock')
        # e.g. « 10 en stock »
        item['stock'] = response.css('.stock::text').get()

        # quantity, e.g. « 15 graines »
        raw_string = response.css(
            '.woocommerce-product-details__short-description p::text'
        ).getall()
        raw_string += response.css('#tab-description td::text').getall()
        item['raw_string'] = ' '.join(raw_string)

        return item


class PromesseDeFleursSpider(scrapy.Spider):
    name = 'promessedefleurs'
    start_urls = ['https://www.promessedefleurs.com/potager/graines-potageres.html']

    def parse(self, response):
        """Process the downloaded response."""
        product_urls = response.css(
            '.product-li .product-image a::attr(href)'
        ).getall()
        for product_url in product_urls:
            yield scrapy.Request(response.urljoin(product_url), self.parse_product)


        next_page_number = 2
        if '?' in response.url:
            return
        while next_page_number < 37:
            # import logging
            # logging.log(logging.WARNING, f"This is a warning {len(product_urls)} : {product_urls[0]}")
            next_page_url = f'{response.url}?p={next_page_number}'
            yield scrapy.Request(response.urljoin(next_page_url))
            next_page_number += 1

    def parse_product(self, response):
        """Analysis of the product page."""
        item = ProductItem()
        item['url'] = response.url
        item['vendor'] = parse_url(response.url).netloc

        item['product_name'] = response.css('h1::text').get()
        item['price'] = response.css('.price > span::text').get()


        return item