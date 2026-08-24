import os

# Configurações de Conexão com o Matrix Switcher
MATRIX_IP = os.getenv("MATRIX_IP", "172.17.100.100")
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

# Mapeamento Oficial de Origens (1 a 64)
ORIGENS_NOMES_DEFAULT = {
    1: "SAT-1", 2: "SAT 2", 3: "EST-1", 4: "EST-2",
    5: "DR-1", 6: "DR-2", 7: "PGM", 8: "PDW1200",
    9: "LiveU-1", 10: "LiveU-2", 11: "LiveU-3", 12: "LiveU-4",
    13: "LiveU-5", 14: "LiveU-6", 15: "LiveU-7", 16: "LiveU-8",
    17: "CRU-1 TECSYS", 18: "CRU-2 SLICE", 19: "SPW1 OUT 1", 20: "SPW1 OUT-2",
    21: "SPW2 OUT-1", 22: "SPW2 OUT-2", 23: "Src 23", 24: "EST1-CL",
    25: "EST2-CL", 26: "SAT1R", 27: "SAT2R", 28: "AJA-1",
    29: "AJA-2", 30: "AJA-6", 31: "COMP EST-1", 32: "COMP EST-2",
    33: "Whats TV", 34: "PLAY1 EST1", 35: "PLAY2 EST1", 36: "PLAY1 EST2",
    37: "PLAY2 EST2", 38: "CAM1 EST1", 39: "CAM2 EST1", 40: "CAM1 EST2",
    41: "CAM2 EST2", 42: "CAM3 EST2", 43: "Eventos1 OUT1", 44: "Eventos1 OUT2",
    45: "Eventos2 OUT1", 46: "Eventos2 OUT2", 47: "ForA OUT-1", 48: "ForA OUT-2",
    49: "ForA OUT-3", 50: "ForA OUT-4", 51: "ForA OUT-5", 52: "ForA OUT-6",
    53: "Fibra-1", 54: "Fibra-2", 55: "Fibra-3", 56: "Fibra-4",
    57: "Fibra-5", 58: "Fibra-6", 59: "Fibra-7", 60: "Fibra-8",
    61: "Fibra-9", 62: "Fibra-10", 63: "Fibra-11", 64: "Fibra-12"
}


# Mapeamento Oficial de Destinos (1 a 64)
DESTINOS_NOMES_DEFAULT = {
    1: "DR-1", 2: "DR-2", 3: "CRU-1 AJA 5", 4: "CRU-2 SLICE",
    5: "PDW1200", 6: "MONITOR MASTER", 7: "SIGNA10", 8: "SIGNA11",
    9: "SIGNA12", 10: "SPW1 IN 1", 11: "SPW2 IN 1", 12: "RTN AR EST-1",
    13: "Encoder SITE .15", 14: "Encoder Mídias .32", 15: "Encoder Evts .33", 16: "LiveU CRU",
    17: "INGEST 1-1", 18: "INGEST 1-2", 19: "INGEST 1-3", 20: "INGEST 1-4",
    21: "INGEST 2-1", 22: "INGEST 2-2", 23: "INGEST 2-3", 24: "INGEST 2-4",
    25: "Dest 25", 26: "Evento 1 IN 1", 27: "Evento 1 IN 2", 28: "Evento 2 IN 1",
    29: "Evento 2 IN 2", 30: "AJA-2 IN 2", 31: "AJA-6 IN-2", 32: "MON CT",
    33: "EST-1 C1", 34: "EST-1 C2", 35: "EST-1 C3", 36: "EST-1 C4",
    37: "EST-1 EXT1", 38: "EST-1 EXT2", 39: "EST-1 VIA 7", 40: "EST-1 VIA 8",
    41: "EST-1 VIA 9", 42: "EST-1 VIA 10", 43: "EST-2 A1", 44: "EST-2 A2",
    45: "EST-2 EXT1", 46: "EST-2 EXT2", 47: "EST-2 VIA 5", 48: "EST-2 VIA 6",
    49: "For.A IN 1", 50: "For.A IN 2", 51: "For.A IN 3", 52: "For.A IN 4",
    53: "For.A IN 5", 54: "For.A IN 6", 55: "MONITOR SALA 19", 56: "COORD VIVO",
    57: "HS6000 IN 21", 58: "HS6000 IN 22", 59: "ATEM-21", 60: "ATEM-22",
    61: "ATEM-23", 62: "ATEM-24", 63: "ATEM-25", 64: "ATEM-26"
}