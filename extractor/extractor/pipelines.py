import re
import time

from w3lib.html import remove_tags
from scrapy.utils.url import parse_url
from scrapy.exceptions import DropItem

from .settings import FORBIDDEN_PRODUCTS


# TODO: fonction `process_items()` : item[key] = fn(item[key])


class DefaultValuesPipeline:
    """
    Defines the default values of the "item" dictionary.
    """
    def process_item(self, item, spider):
        item.setdefault('currency', 'EUR')
        item.setdefault('available', True)
        item.setdefault('promotion', False)
        item.setdefault('weight', 0.)
        item.setdefault('seed_number', 0.)
        item.setdefault('density', 0.)
        item.setdefault('stock', -1),
        item.setdefault('timestamp', int(time.time()))
        return item

class FilterPipeline:
    def process_item(self, item, spider):
        if not item.get('price'):
            raise DropItem('Price required')
        self.filter_product_name(item['product_name'])
        return item

    def filter_product_name(self, product_name):
        """
        Exclude products whose name matches one of the regular
        expressions defined in the constant FORBIDDEN_PRODUCTS
        in settings.
        """
        regex = '|'.join(FORBIDDEN_PRODUCTS)
        pattern = re.compile(rf'(?:{regex})', re.IGNORECASE)
        if re.search(pattern, product_name):
            raise DropItem('Product name unknown')


class BoiteAGrainesPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('laboiteagraines.com'):
            return item
        item['product_name'] = self.parse_name(item['product_name'])
        item['description'] = remove_tags(item['description']).strip()  # laboiteagraines.com
        item['weight'] = self.get_weight(item['description'])
        item['seed_number'] = self.get_seed_number(item['description'])
        return item

    def parse_name(self, name):
        name = name.strip()
        pattern = re.compile(r'\s+bio\s*$', re.IGNORECASE)  # se termine parfois par "bio" ou "BIO", parfois " BIO - ..."
        return re.sub(pattern, '', name)

    def get_seed_number(self, description):
        pattern = re.compile(r'([\d\,\.]+)\s*(?:graines|tubercule)', re.IGNORECASE)
        match = re.search(pattern, description)
        if not match:
            return 0.
        return match.group(1)

    def get_weight(self, description):
        pattern = re.compile(r'\([^\d]*([\d\,\.]+)\s*gramme', re.IGNORECASE)  # laboiteagrainescom
        match = re.search(pattern, description)
        if not match:
            return 0.
        return match.group(1)


class KokopelliPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('kokopelli-semences.fr'):
            return item
        item['seed_number'] = self.get_seed_number(item['raw_string'])
        item['weight'] = self.get_weight(item['raw_string'])
        item['description'] = self.parse_description(item['description'])
        return item

    def get_seed_number(self, string):
        for s in string:
            if re.search(r'(\d+)\sgraines?', s):
                return re.search(r'(\d+)\sgraines?', s).group(1)
        return 0.

    def get_weight(self, string):
        for s in string:
            if re.search(r'(\d+)\sgrammes?', s):
                return re.search(r'(\d+)\sgrammes?', s).group(1)
        return 0.

    def parse_description(self, description):
        return '\n'.join(description)


class BiaugermePipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('biaugerme.com'):
            return item

        item['seed_number'] = self.seed_number_parser(item['raw_string'])
        item['weight'] = self.weight_parser(item['raw_string'])

        item['price'] = self.price_parser(item['price'])
        return item

    def seed_number_parser(self, quantity):
        match = re.search(r'(\d+)\s*grn', quantity)
        if not match:
            return 0.
        return match.group(1)

    def weight_parser(self, quantity):
        match = re.search(r'(\d+)\s*g(?:[^r]|$)', quantity)
        if not match:
            return 0.
        return match.group(1)

    def price_parser(self, price):
        price = re.search(r'([\d\.]+)\s*€', price).group(1)
        return price


class FermedesaintmarthePipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('fermedesaintemarthe.com'):
            return item

        item['product_name'] = self.product_name_parser(item['product_name'])
        #item['price'] = self.parse_price(item['price'])
        #if item.get('old_price'):
            #item['old_price'] = self.parse_price(item['old_price'])
        item = self.get_quantity(item)
        return item

    def product_name_parser(self, product_name):
        """
        Removes unwanted chars at the end of product_name.
        """
        unwanted_strings = (
            r'\s+nt',
            r'\s+ab',
            r'\s+-',
            r'\(\d+ bulbilles?\)',
            r'\s+bio'
        )
        for string in unwanted_strings:
            string += r'(?:\s+|$)'
            regex = re.compile(string, re.IGNORECASE)
            if re.search(regex, product_name):
                product_name = re.sub(regex, '', product_name)
                product_name = product_name.strip()
                product_name = self.product_name_parser(product_name)
        return product_name

    def get_quantity(self, item):
        array = item['raw_string']
        patterns = {
            'gramme': 'weight',
            'graine': 'seed_number',
            'plant': 'seed_number',
            'bulbe': 'seed_number',
            'tubercule': 'seed_number'
        }
        for string in array:
            for pattern, quantity in patterns.items():
                regex = re.compile(rf'(\d+)\s{pattern}', re.IGNORECASE)
                if not re.search(regex, string):
                    continue
                match = re.search(regex, string)
                item[quantity] = match.group(1)
                return item
        raise DropItem('Quantity unknown')


class ComptoirdesgrainesPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('comptoir-des-graines.fr'):
            return item
        
        item['product_name'] = self.product_name_parser(item['product_name'])
        item['product_name'] = self.product_name_parser2(item['product_name'])
        item = self.get_quantity(item)
        return item

    def product_name_parser(self, product_name):
        """
        Sometimes, product names of this shop start with "Graines de".
        It must be removed.
        """
        return re.sub(r'[gG]raines?\sde\s+', '', product_name)

    def get_seed_number(self, string):
        # TODO: useless
        match = re.search(r'(\d+)\sgraines?', string)
        if match:
            string = match.group(1)
        return string

    def product_name_parser2(self, product_name):
        # TODO: duplicata
        """
        Removes unwanted chars at the end of product_name.
        """
        unwanted_strings = (
            r'\s+nt',
            r'\s+ab',
            r'\s+-',
            r'\(\d+ bulbilles?\)',
            r'\s+bio'
        )
        for string in unwanted_strings:
            string += r'(?:\s+|$)'
            regex = re.compile(string, re.IGNORECASE)
            if re.search(regex, product_name):
                product_name = re.sub(regex, '', product_name)
                product_name = product_name.strip()
                product_name = self.product_name_parser(product_name)
        return product_name

    def get_quantity(self, item):
        # TODO: duplicata of FermedesaintmarthePipeline.get_quantity()
        # adapted to string input
        string = item['raw_string']
        patterns = {
            'gramme': 'weight',
            'graine': 'seed_number',
            'plant': 'seed_number',
            'bulbe': 'seed_number',
            'tubercule': 'seed_number'
        }
        regex = re.compile(
            rf"((?:\d+[\.\,])?\d+)\s({'|'.join(patterns.keys())})",
            re.IGNORECASE
        )
        match = re.search(regex, string)
        if match:
            item[patterns[match.group(2)]] = match.group(1)
        return item


class GrainesdeFoliePipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('grainesdefolie.com'):
            return item

        item['product_name'] = self.parse_name(item['product_name'])

        return item

    def parse_name(self, name):
        name = name.strip()
        pattern = re.compile(r'^\s*bio\s+', re.IGNORECASE)  # se termine parfois par "bio" ou "BIO", parfois " BIO - ..."
        return re.sub(pattern, '', name)



class SanRivalPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('sanrivaljardin.com'):
            return item

        item['seed_number'] = self.get_seed_number(item['raw_string'])
        item['weight'] = self.get_weight(item['raw_string'])

        return item

    def get_seed_number(self, string):
        # quasi même fonction que kokopelli
        if re.search(r'(\d+)\sgraines?', string):
            return re.search(r'(\d+)\sgraines?', string).group(1)
        return 0.

    def get_weight(self, string):
        # même pattern que laboiteagraines sans la parenthèse du début
        pattern = r'[^\d]*([\d\,\.]+)\s*gramme'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0.


class GrainesdelPaisPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('grainesdelpais.com'):
            return item

        item['price'] = self.get_price(item['raw_string'])
        item['weight'] = self.get_weight(item['raw_string'])

        return item

    def get_weight(self, string):
        pattern = r'((?:\d+[\.\,])?\d+)\s*g'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0.

    def get_price(self, string):
        pattern = r'((?:\d+[\.\,])?\d+)\s*€'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0.


class GrainesBaumauxPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('graines-baumaux.fr'):
            return item

        item['weight'] = self.get_weight(item['raw_string'])
        if not item['weight']:
            item['weight'] = self.get_weight_from_name(item['product_name'])
        item['product_name'] = self.parse_name(item['product_name'])

        item['price'] = self.get_price(item['price'])
        if (item.get('old_price')):
            item['old_price'] = self.get_price(item['old_price'])
        return item

    def get_weight(self, string):
        if not string: return 0.
        pattern = r'((?:\d+[\.\,])?\d+)\s*g\.'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0.

    def get_weight_from_name(self, string):
        pattern = re.compile(r'(\d+)\s*KILO', re.IGNORECASE)
        if re.search(pattern, string):
            # en kilo !
            return re.search(pattern, string).group(1) + '000'
        return 0.

    def parse_name(self, name):
        name = name.strip()
        pattern = re.compile(r'^\s*bio\s+', re.IGNORECASE)  # se termine parfois par "bio" ou "BIO", parfois " BIO - ..."
        return re.sub(pattern, '', name)

    def get_price(self, string):
        pattern = pattern = r'((?:\d+[\.\,])?\d+)\s*€?'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return ''


class PotagerEtGourmandsPipeline:
    def process_item(self, item, spider):
        if not item['vendor'].endswith('potage-et-gourmands.fr'):
            return item

        item['stock'] = self.get_stock(item['stock'])
        item['weight'] = self.get_weight(item['raw_string'])
        return item

    def get_stock(self, string):
        if not string:
            return 0
        pattern = r'(\d+)\s*en\sstock'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0

    def get_weight(self, string):
        if string is None:
            raise DropItem('Weight required')
        pattern = r'(\d*[\.\,]?\d+)\s*gramme'
        if re.search(pattern, string):
            return re.search(pattern, string).group(1)
        return 0.


class FormattingPipeline:
    def process_item(self, item, spider):
        item.setdefault('old_price', item['price']) 
        item['product_name'] = self.case_fix(item['product_name'])

        item['price'] = self.to_float(item['price'])
        item['old_price'] = self.to_float(item['old_price'])
        item['weight'] = self.to_float(item['weight'])
        item['seed_number'] = self.to_float(item['seed_number'])
        item['density'] = self.to_float(item['density'])
        if item.get('raw_string'):
            del item['raw_string']
        item['stock'] = self.to_int(item['stock'])
        return item

    def case_fix(self, string):
        """
        Capitalize a string if it is only composed of uppercase
        or only lowercase letters.
        """
        compact_string = re.sub(r'[^A-Za-z]', '', string)
        if all(letter.isupper() for letter in compact_string):
            return string.capitalize()
        if all(letter.islower() for letter in compact_string):
            return string.capitalize()
        return string

    def to_float(self, string):
        if not isinstance(string, str):
            return string
        string = string.replace(',', '.')
        return float(string)

    def to_int(self, string):
        if not isinstance(string, str):
            return string
        return int(string)