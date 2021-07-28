import pytest

from extractor.pipelines import FermedesaintmarthePipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('ALFALFA BIO', 'ALFALFA'),
        ('alfalfa bio', 'alfalfa'),
        ('ALLIAIRE OFFICINALE NT', 'ALLIAIRE OFFICINALE'),
        ('ALIMENT', 'ALIMENT'),
        ('ANETH OFFICINALE AB', 'ANETH OFFICINALE'),
        ('AUBERGINE VIOLETTA LUNGA 3 AB', 'AUBERGINE VIOLETTA LUNGA 3'),
        ('BASILIC SACRE OU TULSI AB', 'BASILIC SACRE OU TULSI'),
        ('BASILIC SACRE OU TULSI - AB', 'BASILIC SACRE OU TULSI'),
        ('AIL ROCAMBOLE NT (3 bulbilles)', 'AIL ROCAMBOLE'),
    ]
)
def test_product_name_parsing(input, output):
    pipeline = FermedesaintmarthePipeline()
    assert pipeline.product_name_parser(input) == output