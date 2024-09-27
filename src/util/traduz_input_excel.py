import os

import numpy as np
import pandas as pd


class SeparatorNotFoundError(Exception):
    """
    Classe de erro para o caso onde nenhum dos candidatos a separador era possível ser usado na conversão para csv.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"SeparatorNotFoundError: {self.message}"


input_path = 'data/input/'

# acha todos os arquivos na pasta de input
arquivos = [f for f in os.listdir(
    input_path) if os.path.isfile(os.path.join(input_path, f))]


def acha_caractere_em_df(df, caracter) -> bool:
    '''
    procura para ver se um caractere especifico existe em um df,
    para que saiba se este caracter pode ser usado como separador em um csv
    '''
    tem_caracter = df.apply(
        lambda col: col.astype(str).str.contains(caracter).any(), axis=0
    )
    return tem_caracter.any()


separadores = [',', ';', '|', '/', '&', '$', '%', '@', '#', '£', '¢', '§']

# data frame para poder serem salvos os separadores usados em cada exportação

try:
    exportacoes = pd.read_csv(input_path + 'separadores.csv', encoding='utf-8')
except:
    exportacoes = pd.DataFrame({
        'file': [],
        'sep': []
    })

separadores_a_guardar = []


for arquivo in arquivos:
    nome_arquivo, extensao = arquivo.split('.')
    extensao = '.' + extensao
    if extensao.lower() != '.xlsx':
        if extensao.lower() == '.csv':
            if nome_arquivo == 'separadores':
                continue
            separadores_a_guardar.append(nome_arquivo.lower() + '.xlsx')
        continue

    # seria ideal testar se o arquivo já foi traduzido antes de tentar traduzí-lo
    if nome_arquivo + '.csv' in arquivos:
        continue

    print(arquivo, 'está sendo traduzido.\n')
    # trata o bd acidentes não ser chamado Sheet1 nem ser a primeira sheet
    if 'acid' in nome_arquivo.lower():
        try:
            df = pd.read_excel(input_path + arquivo,
                               sheet_name='Acidentes', engine='calamine')
        except ValueError:
            pass
    else:
        try:
            df = pd.read_excel(input_path + arquivo, engine='calamine')

        except:
            print("erro lendo o arquivo.")
            exit(1)

    conseguiu_exportar = False
    for c in separadores:
        tem_caractere = acha_caractere_em_df(df, c)
        print(tem_caractere, c, 'existe na tabela', arquivo)
        if not tem_caractere:
            conseguiu_exportar = True
            df.to_csv(input_path + nome_arquivo +
                      '.csv', sep=c, encoding='utf-8', index=False)
            if arquivo in exportacoes['file'].unique():
                exportacoes.loc[exportacoes['file'] == arquivo, 'sep'] = c
                separadores_a_guardar.append(arquivo.lower())
            else:
                exportacoes.loc[len(exportacoes)] = {
                    'file': arquivo,
                    'sep': c
                }
                separadores_a_guardar.append(arquivo.lower())
            break

    if conseguiu_exportar:
        print(arquivo, 'exportado para csv usando', c, 'como separador.')
        continue
    else:
        raise SeparatorNotFoundError(
            f'No arquivo {arquivo} não foi encontrado um separador possível para a exportação à .csv\n')

exportacoes.replace({',': np.nan}, inplace=True)

print(separadores_a_guardar)

# bacalhau
mask = exportacoes['file'].str.lower().isin(separadores_a_guardar)
exportacoes = exportacoes[mask]

print(exportacoes)

exportacoes.to_csv(input_path + 'separadores.csv',
                   encoding='utf-8', index=False)
