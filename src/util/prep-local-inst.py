import pandas as pd

# criacao do df de local/coordenada a partir das novas tabelas
pathIn = "dados/input/"
pathOut = "dados/util/"

df_coord_instalacoes = pd.read_excel(pathIn + "ESUL-LIs-exceto linhas.xlsx")
# reduzindo as colunas que não serão utilizadas
df_coord_instalacoes = df_coord_instalacoes[
    ["Local de instalação", "Latitude", "Longitude"]
]


# cria um dicionario que consegue ser utilizado em um .replace() para conseguir
# agrupar as siglas de subestação checando se a string da sigla pertence a string de outra sigla na coluna
def agrupa_siglas_de_instalacao(dfLocais, colSigla, lista_siglas=None):

    dictTraducoes = {}

    if lista_siglas == None:
        lista_siglas = dfLocais[colSigla].dropna(inplace=True)
        lista_siglas = dfLocais[colSigla].unique()

    para_substituir = dfLocais[colSigla].unique()
    for sigla in lista_siglas:
        for subconjunto in para_substituir:
            if sigla in subconjunto:
                if subconjunto not in dictTraducoes:
                    dictTraducoes[subconjunto] = sigla
                else:
                    if sigla in dictTraducoes[subconjunto]:
                        dictTraducoes[subconjunto] = sigla
    return dictTraducoes


def cria_df_nomes_unicos(dfLocalComScore, colSigla):

    # reconstroi o dfLocalComScore agrupando as linhas que usam a mesma sigla

    df = pd.DataFrame()

    df[colSigla] = dfLocalComScore[colSigla].dropna().unique()

    for i, row in df.iterrows():
        sigla = df.loc[i, colSigla]
        idx = dfLocalComScore.index[dfLocalComScore[colSigla] == sigla].to_list()
        df.loc[i, "Latitude"] = dfLocalComScore.loc[idx[0], "Latitude"]
        df.loc[i, "Longitude"] = dfLocalComScore.loc[idx[0], "Longitude"]

    return df


# preprocessando as coordenadas deste df
df_coord_instalacoes["Latitude"] = (
    df_coord_instalacoes["Latitude"].str.replace(",", ".").str.replace("°", "")
)
df_coord_instalacoes["Longitude"] = (
    df_coord_instalacoes["Longitude"].str.replace(",", ".").str.replace("°", "")
)
df_coord_instalacoes["Latitude"] = df_coord_instalacoes["Latitude"].astype(float)
df_coord_instalacoes["Longitude"] = df_coord_instalacoes["Longitude"].astype(float)

df_siglas_importantes = df_coord_instalacoes.dropna(subset=["Latitude", "Longitude"])

dict_traducao = agrupa_siglas_de_instalacao(
    df_siglas_importantes, "Local de instalação"
)

# criando os locais de maneira unívoca
df_coord_instalacoes.dropna(subset=["Latitude", "Longitude"], inplace=True)
df_coord_instalacoes.replace(dict_traducao, inplace=True)
df_coord_instalacoes = cria_df_nomes_unicos(df_coord_instalacoes, "Local de instalação")

df_coord_instalacoes.to_csv(pathOut + "instalacao_coordenada.csv")
