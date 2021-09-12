import pytest

from extractor.pipelines import BoiteAGrainesPipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('tomate bio', 'tomate'),
        ('tomate BIO', 'tomate'),
        (' tomate bio', 'tomate'),
        (' tomate BIO', 'tomate'),
        ('tomate bio ', 'tomate'),
        (' tomate BIO ', 'tomate'),
        ('tomate', 'tomate'),
        ('tomate bio orange', 'tomate bio orange'),
        ('tomatebio orange', 'tomatebio orange')
    ]
)
def test_product_name_parsing(input, output):
    pipeline = BoiteAGrainesPipeline()
    assert pipeline.parse_name(input) == output


@pytest.mark.parametrize(
    'description,quantity',
    [
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAMME = +/- 50 GRAINES)', '50'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAMME = +/- 50 graines)', '50'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAMME = +/- 50 TUBERCULES)', '50'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAMME = +/- 50 tubercules)', '50'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAMME = +/- 50 grammes)', 0.0),
    ]
)
def test_seed_number(description, quantity):
    pipeline = BoiteAGrainesPipeline()
    assert pipeline.get_seed_number(description) == quantity

@pytest.mark.parametrize(
    'description,weight',
    [
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 grammes = +/- 50 TUBERCULES)', '0,2'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRamme = +/- 50 tubercules)', '0,2'),
        ('On peut les utiliser pour faire des ratatouilles, en beignets, sautées à la poêle. Variété non inscrite (0,2 GRAINES = +/- 50 graines)', 0.0),
    ]
)
def test_weight(description, weight):
    pipeline = BoiteAGrainesPipeline()
    assert pipeline.get_weight(description) == weight