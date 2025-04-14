import os

def criar_diretorios(inDir, latitude, longitude, area):
    if not os.path.exists(inDir):
        os.makedirs(inDir)
    _localdataName = f"{inDir}/{latitude}_{longitude}_{area}"
    if not os.path.exists(_localdataName):
        os.makedirs(_localdataName)
    _graficos = os.path.join(_localdataName, "resultados")
    if not os.path.exists(_graficos):
        os.makedirs(_graficos)
    return _localdataName, _graficos

def obter_caminhos_graficos(latitude, longitude, _res, _ano_inicial, _ano_final):
    """
    Gera os caminhos para os gráficos e mapas gerados.
    """
    grafico_precipitacao_path = os.path.join(
        f"cache_data/{latitude}_{longitude}_{_res}/resultados/grafico_precipitacao_Região_Nordeste_-_Brasil_{_ano_inicial}_{_ano_final}.png"
    ).replace("\\", "/")
    grafico_rai_path = os.path.join(
        f"cache_data/{latitude}_{longitude}_{_res}/resultados/RAI.png"
    ).replace("\\", "/")
    grafico_aridez_path = os.path.join(
        f"cache_data/{latitude}_{longitude}_{_res}/resultados/IA.png"
    ).replace("\\", "/")
    mapaIA_path = os.path.join(
        f"cache_data/{latitude}_{longitude}_{_res}/resultados/mapaIA{_ano_inicial}-{_ano_final}.png"
    ).replace("\\", "/")

    print(f"Gráfico de precipitação salvo em: {grafico_precipitacao_path}")
    print(f"Gráfico de RAI salvo em: {grafico_rai_path}")
    print(f"Gráfico de aridez salvo em: {grafico_aridez_path}")
    print(f"Mapa de IA salvo em: {mapaIA_path}")

    return grafico_precipitacao_path, grafico_rai_path, grafico_aridez_path, mapaIA_path