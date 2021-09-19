import pytest

from extractor.pipelines import GrainesBaumauxPipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('0,25 g. NT', '0,25'),
        ('', 0.),
        (None, 0.)
    ]
)
def test_weight_parsing(input, output):
    pipeline = GrainesBaumauxPipeline()
    assert pipeline.get_weight(input) == output

@pytest.mark.parametrize(
    'input,output',
    [
        ('5.5', '5.5'),
        ('7.5 €', '7.5'),
        ('5,50\xa0€', '5,50')
    ]
)
def test_price_parsing(input, output):
    pipeline = GrainesBaumauxPipeline()
    assert pipeline.get_price(input) == output

@pytest.mark.parametrize(
    'input,output',
    [
        ('tomate 5 KILOS', '5000'),
        ('tomates 5 GRAMMES', 0.)
    ]
)
def test_weight_from_name(input, output):
    pipeline = GrainesBaumauxPipeline()
    assert pipeline.get_weight_from_name(input) == output