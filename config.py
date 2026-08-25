import os

# Configurações de Conexão com o Matrix Switcher
MATRIX_IP = os.getenv("MATRIX_IP", "192.168.0.2")
MATRIX_PORT = int(os.getenv("MATRIX_PORT", 80))

# Mapeamento dos dias da semana (0 = Segunda, 6 = Domingo)
MAP_DIAS_INDEX = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}

# Mapeamento Padrão de Fábrica das Origens (Entradas 1 a 64)
# Aponta dinamicamente para a chave 'default_input_label' do locales.py
ORIGENS_NOMES_DEFAULT = {
    i: f"default_input_label:{i}" for i in range(1, 65)
}

# Mapeamento Padrão de Fábrica dos Destinos (Saídas 1 a 64)
# Aponta dinamicamente para a chave 'default_output_label' do locales.py
DESTINOS_NOMES_DEFAULT = {
    i: f"default_output_label:{i}" for i in range(1, 65)
}
