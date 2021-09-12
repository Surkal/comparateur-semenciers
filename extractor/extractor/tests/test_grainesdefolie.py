import pytest

from extractor.pipelines import GrainesdeFoliePipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('bio tomate', 'tomate'),
        ('BIO tomate', 'tomate'),
        ('BIO tomate ', 'tomate'),
        ('BIO TOMATE', 'TOMATE'),
        ('bio tomate ', 'tomate'),
        ('tomate bio ', 'tomate bio'),
        (' tomate BIO ', 'tomate BIO'),
        ('tomate', 'tomate'),
        ('tomate bio orange', 'tomate bio orange'),
        ('tomatebio orange', 'tomatebio orange'),
        ('tomate biorange', 'tomate biorange')
    ]
)
def test_product_name_parsing(input, output):
    pipeline = GrainesdeFoliePipeline()
    assert pipeline.parse_name(input) == output