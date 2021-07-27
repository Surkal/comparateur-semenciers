import re

from w3lib.html import remove_tags
from scrapy.utils.url import parse_url
from scrapy.exceptions import DropItem


class FilterPipeline:
    def process_item(self, item, spider):
        item['weight'] = item.get('weight', 0)
        item['seed_number'] = item.get('seed_number', 0)
        if not item.get('price'):
            raise DropItem
        return item

class BoiteAGrainesPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('laboiteagraines.com'):
            return item
        item['price'] = self.parse_price(item['price'])
        item['product_name'] = self.parse_name(item['product_name'])
        item['description'] = remove_tags(item['description']).strip()  # laboiteagraines.com
        item['weight'] = self.get_weight(item['description'])
        item['seed_number'] = self.get_seed_number(item['description'])
        return item

    def parse_name(self, name):
        name = name.strip()
        pattern = re.compile(r'\s*bio(\s.*)?$', re.IGNORECASE)  # se termine parfois par "bio" ou "BIO", parfois " BIO - ..."
        return re.sub(pattern, '', name)

    def parse_price(self, price):
        price = price.replace(',', '.')
        return float(price)

    def get_seed_number(self, description):
        pattern = re.compile(r'([\d\,\.]+)\s*(?:graines|tubercule)', re.IGNORECASE)
        match = re.search(pattern, description)
        if not match:
            return 0
        number = match.group(1).replace(',', '.')  # TODO: même fonction que self.parse_price()
        return float(number)

    def get_weight(self, description):
        pattern = re.compile(r'\([^\d]*([\d\,\.]+)\s*gramme', re.IGNORECASE)  # laboiteagrainescom
        match = re.search(pattern, description)
        if not match:
            return 0
        weight = match.group(1).replace(',', '.')  # TODO: même fonction que self.parse_price()
        return float(weight)


class KokopelliPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('kokopelli-semences.fr'):
            return item
        item['seed_number'] = self.get_seed_number(item['raw_string'])
        item['weight'] = self.get_weight(item['raw_string'])
        item['description'] = self.parse_description(item['description'])

        del item['raw_string']
        return item

    def get_seed_number(self, string):
        for s in string:
            if re.search(r'(\d+)\sgraines?', s):
                return float(re.search(r'(\d+)\sgraines?', s).group(1))
        return 0.0

    def get_weight(self, string):
        for s in string:
            if re.search(r'(\d+)\sgrammes?', s):
                return float(re.search(r'(\d+)\sgrammes?', s).group(1))
        return 0.0

    def parse_description(self, description):
        return '\n'.join(description)


class BiaugermePipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('biaugerme.com'):
            return item

        item['seed_number'] = self.seed_number_parser(item['raw_string'])
        item['weight'] = self.weight_parser(item['raw_string'])
        del item['raw_string']

        item['density'] = self.get_density(item['density'])
        item['price'] = self.price_parser(item['price'])
        return item

    def get_density(self, density):
        if not density:
            return 0
        return int(density)

    def seed_number_parser(self, quantity):
        match = re.search(r'(\d+)\s*grn', quantity)
        if not match:
            return 0.
        return float(match.group(1))

    def weight_parser(self, quantity):
        match = re.search(r'(\d+)\s*g(?:[^r]|$)', quantity)
        if not match:
            return 0.
        return float(match.group(1))

    def price_parser(self, price):
        price = re.search(r'([\d\.]+)\s*€', price).group(1)
        return float(price)