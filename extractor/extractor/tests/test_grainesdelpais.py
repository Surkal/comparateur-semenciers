import pytest

from extractor.pipelines import GrainesdelPaisPipeline

@pytest.mark.parametrize(
    'string,weight,price',
    [
        ('40 g - 3.40 €', '40', '3.40'),
        ('0.8 g - 2.40 €', '0.8', '2.40'),
    ]
)
def test_parser(string, weight, price):
    pipeline = GrainesdelPaisPipeline()
    assert pipeline.get_weight(string) == weight
    assert pipeline.get_price(string) == price