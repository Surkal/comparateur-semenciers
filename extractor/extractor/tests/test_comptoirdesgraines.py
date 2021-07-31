import pytest

from extractor.pipelines import ComptoirdesgrainesPipeline


@pytest.mark.parametrize(
    'string,weight,seed_number',
    [
        ('Sachet de 12 graines', None, '12'),
        ('Sachet de 4 grammes', '4', None),
        ('Sachet de 0.1 gramme', '0.1', None),
        ('Sachet de 0,1 gramme', '0,1', None),
        ('1 portion', None, None),
    ]
)
def test_get_quantity(string, weight, seed_number):
    pipeline = ComptoirdesgrainesPipeline()
    item = {'raw_string': string}
    item = pipeline.get_quantity(item)
    assert item.get('weight') == weight
    assert item.get('seed_number') == seed_number