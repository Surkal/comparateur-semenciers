import re

import pytest
from scrapy.exceptions import DropItem

from extractor.pipelines import FilterPipeline
from extractor.settings import FORBIDDEN_PRODUCTS


@pytest.mark.parametrize(
    'product_name,result',
    [
        ('mélange de fleurs', True),
        ('fleurs en melanges', True),
        ('assortiment de fleurs', True),
        ('tomate', False),
        ('tomate jaune', False),
        # ... et ...
        ('betteraves', False),
        ('Carottes et radis', True),
    ]
)
def test_filter_product(product_name, result):
    if result:
        with pytest.raises(DropItem) as e:
            FilterPipeline().filter_product_name(product_name)
    else:
        FilterPipeline().filter_product_name(product_name)