import pandas as pd
from resolve_path import read_input


def keep_columns(df: pd.DataFrame, columns: list):
    '''
    Retorna um novo DataFrame com apenas as colunas passadas como argumento
    '''
    return df[columns]


def drop_nan(df: pd.DataFrame, columns: list):
    '''
    Retorna um novo DataFrame sem as linhas que possuem NaN em alguma das colunas passadas como argumento
    '''
    return df.dropna(subset=columns, how="any")


def float_coords(df: pd.DataFrame):
    '''
    Transforma as colunas de Latitude e Longitude em float
    '''
    df["latitude"] = df["latitude"].str.replace(
        ",", ".").str.replace("°", "").astype(float)
    df["longitude"] = df["longitude"].str.replace(
        ",", ".").str.replace("°", "").astype(float)

    return df


def get_ponto_central(df):
    '''
    Retorna o vão central de uma Linha de Transmissão
    '''

    lt = "!"
    vaos = []

    for index, row in df.iterrows():
        new_parts = row["local_de_instalacao"].split("-")
        new_lt = "-".join(new_parts[:5])

        if lt != new_lt:
            tam_vaos = len(vaos)
            idx_meio = tam_vaos//2

            if tam_vaos >= 1:
                centro = vaos[idx_meio]
                l_strings = centro[0].split("-")
                centro[0] = "-".join(l_strings[:5])

                centro_df = pd.DataFrame(
                    [centro], columns=["local_de_instalacao", "latitude", "longitude"])
                df = pd.concat([df, centro_df], ignore_index=True)

            lt = new_lt
            vaos = []

        vaos.append([row["local_de_instalacao"],
                    row["latitude"], row["longitude"]])

    tam_vaos = len(vaos)
    idx_meio = tam_vaos//2

    l_strings = vaos[idx_meio][0].split("-")
    vaos[idx_meio][0] = "-".join(l_strings[:5])

    if tam_vaos >= 1:
        centro = vaos[idx_meio]
        centro_df = pd.DataFrame(
            [centro], columns=["local_de_instalacao", "latitude", "longitude"])
        df = pd.concat([df, centro_df], ignore_index=True)

    return df


pathOut = "data/util/"

df_lt = read_input("ESUL-LIs-LTs e vaos torres.csv")
df_li = read_input("ESUL-LIs-exceto linhas.csv")


# preprocessa as colunas que serão usadas
df_lt = df_lt.rename(columns={"Local de instalação": "local_de_instalacao",
                              "Latitude": "latitude",
                              "Longitude": "longitude",
                              })

df_li = df_li.rename(columns={"Local de instalação": "local_de_instalacao",
                              "Latitude": "latitude",
                              "Longitude": "longitude",
                              })

df_lt = keep_columns(df_lt, ["local_de_instalacao", "latitude", "longitude"])
df_lt = drop_nan(df_lt, ["latitude", "longitude"])
df_lt = float_coords(df_lt)
df_lt = df_lt.sort_values(by=["local_de_instalacao"])
df_lt = get_ponto_central(df_lt)
df_lt = df_lt.sort_values(by=["local_de_instalacao"])

df_li = keep_columns(df_li, ["local_de_instalacao", "latitude", "longitude"])
df_li = drop_nan(df_li, ["latitude", "longitude"])
df_li = float_coords(df_li)
df_li = df_li.sort_values(by=["local_de_instalacao"])


# junta as informações de subestações e de linhas de transmissão em um
# dataframe de locais de instalação unificado
df_coordenadas = pd.concat([df_li, df_lt], axis=0)

df_coordenadas.to_csv(pathOut + "local_coordenada.csv",
                      sep=";", index=False, encoding="utf-8")
