import pytest

from extractor.pipelines import BiaugermePipeline


@pytest.mark.parametrize(
    'string,weight,seed_number',
    [
        ('2 g', '2', 0.),
        ('12 g', '12', 0.),
        ('12 grn', 0., '12'),
        ('2 grn', 0., '2'),
    ]
)
def test_quantity_parsing(string, weight, seed_number):
    pipeline = BiaugermePipeline()
    assert pipeline.weight_parser(string) == weight
    assert pipeline.seed_number_parser(string) == seed_number