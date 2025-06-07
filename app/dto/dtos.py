class ResultadosDTO:
    def __init__(self, nome_local, ano_inicial, ano_final, area, latitude, longitude,
                 dados_grafico_precipitacao, dados_grafico_precipitacao_vs_evaporacao, 
                 dados_grafico_balanco_hidrico, dados_grafico_rai, dados_grafico_aridez, 
                 mapa_IA, indices_e_classificacoes, recomendacoes):
        self.nome_local = nome_local
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final
        self.area = area
        self.latitude = latitude
        self.longitude = longitude
        self.dados_grafico_precipitacao = dados_grafico_precipitacao
        self.dados_grafico_precipitacao_vs_evaporacao = dados_grafico_precipitacao_vs_evaporacao
        self.dados_grafico_balanco_hidrico = dados_grafico_balanco_hidrico
        self.dados_grafico_rai = dados_grafico_rai
        self.dados_grafico_aridez = dados_grafico_aridez
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
            "dados_grafico_precipitacao": self.dados_grafico_precipitacao,
            "dados_grafico_precipitacao_vs_evaporacao": self.dados_grafico_precipitacao_vs_evaporacao,
            "dados_grafico_balanco_hidrico": self.dados_grafico_balanco_hidrico,
            "dados_grafico_rai": self.dados_grafico_rai,
            "dados_grafico_aridez": self.dados_grafico_aridez,
            "mapa_IA": self.mapa_IA,
            "indices_e_classificacoes": self.indices_e_classificacoes,
            "recomendacoes": self.recomendacoes,
        }
    
class ProcessarDadosDTO:
    def __init__(self, latitude, longitude, cultura, estagio, head, user_id, ano_inicial=2004, ano_final=2024):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.cultura = cultura
        self.estagio = estagio
        self.head = head
        self.ano_inicial = ano_inicial
        self.ano_final = ano_final
        self.user_id = user_id