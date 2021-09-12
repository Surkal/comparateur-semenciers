import pytest

from extractor.pipelines import SanRivalPipeline


raw_string = ("Très parfumées pour vos assaisonnements et infusions. Ses "
              "feuilles disparaissent quand vient l'hiver. C'est aussi un "
              "très bon anti stress ! Quantité \xa0:  0,3 gramme soit environ "
              "1800 graines. Période de semis :\xa0 d’avril à juin directement "
              "en place, en ligne. Période de récolte \xa0: \xa0 dès la fin du "
              "premier été, puis pendant toute la période de végétation, les "
              "feuilles et les jeunes pousses. Conseil culinaire \xa0L'estragon "
              "est idéal dans l'élaboration de vos sauces qui agrémenteront vos "
              "sauces à merveille pour vos poissons.\xa0 Sans oublier le fameux "
              "poulet à l'estragon de mamie Jacqueline. Quantité   Partager    "
              "\xa0     \xa0  Originaire de Sibérie et de Chine l'estragon a "
              "souvent été appelé dragon verre du a ses racines.\xa0 0253 95 "
              "Produits")

def test_get_seed_number():
    pipeline = SanRivalPipeline()
    assert pipeline.get_seed_number(raw_string) == '1800'

def test_get_weight():
    pipeline = SanRivalPipeline()
    assert pipeline.get_weight(raw_string) == '0,3'