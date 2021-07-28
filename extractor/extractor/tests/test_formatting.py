import pytest

from extractor.pipelines import FormattingPipeline


@pytest.mark.parametrize(
    'input,output',
    [
        ('AIL', 'Ail'),
        ('AIL DES OURS', 'Ail des ours'),
        ('ail', 'Ail'),
        ('Ail des Ours', 'Ail des Ours'),
        ('TomAtE', 'TomAtE'),
    ]
)
def test_case_fix(input, output):
    pipeline = FormattingPipeline()
    assert pipeline.case_fix(input) == output