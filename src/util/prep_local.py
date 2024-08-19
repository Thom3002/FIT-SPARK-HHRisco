import pandas as pd
from resolve_path import ajuste_path, read_input

pathIn = "data/input/"
pathOut = "data/util/"

df_lts = read_input(
    pathIn + "ESUL-LIs-LTs e vaos torres.csv")


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
    df["Latitude"] = df["Latitude"].str.replace(
        ",", ".").str.replace("°", "").astype(float)
    df["Longitude"] = df["Longitude"].str.replace(
        ",", ".").str.replace("°", "").astype(float)

    return df


pathIn = "data/input/"
pathOut = "data/util/"

df_lts = pd.read_excel(
    pathIn + "ESUL-LIs-LTs e vaos torres.xlsx", engine="calamine")
df_lis = pd.read_excel(
    pathIn + "ESUL-LIs-exceto linhas.XLSX", engine="calamine")

df_lts = keep_columns(df_lts, ["Local de instalação", "Latitude", "Longitude"])
df_lts = drop_nan(df_lts, ["Latitude", "Longitude"])
df_lts = float_coords(df_lts)

df_lis = keep_columns(df_lis, ["Local de instalação", "Latitude", "Longitude"])
df_lis = drop_nan(df_lis, ["Latitude", "Longitude"])
df_lis = float_coords(df_lis)

df_coordenadas = pd.concat([df_lis, df_lts], axis=0)

df_coordenadas.to_csv(pathOut + "local_coordenada.csv",
                      sep=";", index=False, encoding="utf-8")
