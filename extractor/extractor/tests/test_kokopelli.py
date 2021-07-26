import pytest

from extractor.pipelines import KokopelliPipeline


@pytest.mark.parametrize(
    'description_array,description',
    [
        (['one', 'two'], 'one\ntwo'),
    ]
)
def test_description_parsing(description_array, description):
    pipeline = KokopelliPipeline()
    assert pipeline.parse_description(description_array) == description

@pytest.mark.parametrize(
    'string,value',
    [
        (['one', 'Contenance du Sachet : 35 graines', '42 graines'], 35.0),
        (['one', 'Contenance du Sachet : 35 grammes', '42 grammes'], 0.0),
    ]
)
def test_get_seed_number(string, value):
    pipeline = KokopelliPipeline()
    assert pipeline.get_seed_number(string) == value

@pytest.mark.parametrize(
    'string,value',
    [
        (['one', 'Contenance du Sachet : 35 graines', '42 graines'], 0.0),
        (['one', 'Contenance du Sachet : 35 grammes', '42 grammes'], 35.0),
    ]
)
def test_get_weight(string, value):
    pipeline = KokopelliPipeline()
    assert pipeline.get_weight(string) == value