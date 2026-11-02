import config


def test_portas_cobrem_a_matriz_inteira():
    assert sorted(config.ORIGENS_NOMES_DEFAULT) == list(range(1, 65))
    assert sorted(config.DESTINOS_NOMES_DEFAULT) == list(range(1, 65))


def test_dias_da_semana_cobrem_de_segunda_a_domingo():
    assert sorted(config.MAP_DIAS_INDEX) == list(range(7))
