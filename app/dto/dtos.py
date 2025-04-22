class ResultadosDTO:
    def __init__(self, nome_local, ano_inicial, ano_final, area, latitude, longitude,
                 grafico_precipitacao, grafico_precipitacao_vs_evaporacao, grafico_balanco_hidrico, grafico_rai, grafico_aridez, mapa_IA, indices_e_classificacoes, recomendacoes):
        self.nome_local = nome_local
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final
        self.area = area
        self.latitude = latitude
        self.longitude = longitude
        self.grafico_precipitacao = grafico_precipitacao
        self.grafico_precipitacao_vs_evaporacao = grafico_precipitacao_vs_evaporacao
        self.grafico_balanco_hidrico = grafico_balanco_hidrico
        self.grafico_rai = grafico_rai
        self.grafico_aridez = grafico_aridez
        self.mapa_IA = mapa_IA
        self.indices_e_classificacoes = indices_e_classificacoes
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
            "grafico_precipitacao_vs_evaporacao": self.grafico_precipitacao_vs_evaporacao,
            "grafico_balanco_hidrico": self.grafico_balanco_hidrico,
            "grafico_rai": self.grafico_rai,
            "grafico_aridez": self.grafico_aridez,
            "mapa_IA": self.mapa_IA,
            "indices_e_classificacoes": self.indices_e_classificacoes,
            "recomendacoes": self.recomendacoes,
        }
    
class ProcessarDadosDTO:
    def __init__(self, latitude, longitude, cultura, estagio, head, user_id, ano_inicial=2020, ano_final=2022):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.cultura = cultura
        self.estagio = estagio
        self.head = head
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final
        self.user_id = user_id