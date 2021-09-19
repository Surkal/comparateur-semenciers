import pytest
from scrapy.exceptions import DropItem

from extractor.pipelines import PotagerEtGourmandsPipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('5 en stock', '5'),
        ('10 en stock', '10'),
        ('', 0),
        (None, 0)
    ]
)
def test_stock_parsing(input, output):
    pipeline = PotagerEtGourmandsPipeline()
    assert pipeline.get_stock(input) == output

@pytest.mark.parametrize(
    'input,output',
    [
        ('Paquet de 3 grammes', '3'),
        ('Paquet de 1 gramme', '1'),
        ('Saquet de 0,3 grammes', '0,3'),
        ('Paquet de 0.3 grammes', '0.3')
    ]
)
def test_weight_parser(input, output):
    pipeline = PotagerEtGourmandsPipeline()
    assert pipeline.get_weight(input) == output

def test_dropping_cause_no_weight():
    pipeline = PotagerEtGourmandsPipeline()
    with pytest.raises(DropItem) as e:
        pipeline.get_weight(None)