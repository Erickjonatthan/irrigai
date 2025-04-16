class ResultadosDTO:
    def __init__(self, nome_local, ano_inicial, ano_final, area, latitude, longitude,
                 grafico_precipitacao, grafico_rai, grafico_aridez, mapa_IA, recomendacoes):
        self.nome_local = nome_local
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final
        self.area = area
        self.latitude = latitude
        self.longitude = longitude
        self.grafico_precipitacao = grafico_precipitacao
        self.grafico_rai = grafico_rai
        self.grafico_aridez = grafico_aridez
        self.mapa_IA = mapa_IA
        self.recomendacoes = recomendacoes

    def to_dict(self):
        return {
            "nome_local": self.nome_local,
            "ano_inicial": self.ano_inicial,
            "ano_final": self.ano_final,
            "area": self.area,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "grafico_precipitacao": self.grafico_precipitacao,
            "grafico_rai": self.grafico_rai,
            "grafico_aridez": self.grafico_aridez,
            "mapa_IA": self.mapa_IA,
            "recomendacoes": self.recomendacoes,
        }
    
class ProcessarDadosDTO:
    def __init__(self, latitude, longitude, cultura, estagio, head, ano_inicial=2022, ano_final=2023):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.cultura = cultura
        self.estagio = estagio
        self.head = head
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final