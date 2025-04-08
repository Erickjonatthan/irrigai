import os
import pandas as pd
import requests
import climateservaccess as ca

def status(id_tarefa, api, head):
    return requests.get(f'{api}task/{id_tarefa}', headers=head).json()['status']

def precipitacao_ano(ano, _quadrado, _localdataName):
    """
    Processa os dados de precipitação para um ano específico.
    """
    arqName = f"{_localdataName}/{ano} precipit data.csv"
    data_type = 26  # Dados de precipitação
    start_date = f"01/01/{ano}"
    end_date = f"12/31/{ano}"
    operation_type = 'average'
    polygon = _quadrado

    if os.path.exists(arqName):
        print(f"Arquivo do ano de {ano} já baixado, carregando arquivos locais ...")
        df = pd.read_csv(arqName + ".raw")
        return df['raw_value']
    else:
        df = ca.getDataFrame(data_type, start_date, end_date, operation_type, polygon)
        df.to_csv(arqName)
        data_df = pd.DataFrame(df['data'].to_list())
        data_df['raw_value'].to_csv(arqName + ".raw")
        return data_df['raw_value']