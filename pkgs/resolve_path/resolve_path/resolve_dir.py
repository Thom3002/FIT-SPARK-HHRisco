import os

import numpy as np
import pandas as pd


def ajuste_path(path):
    '''
    Função que descobre de onde o código está sendo rodado,
    dentro do repositório FIT-SPARK-HHRisco e adiciona o backtrack necessário para chegar ao root.
    '''

    cwd = os.getcwd()
    cwd = cwd.replace('\\', '/')

    nome_repo = 'FIT-SPARK-HHRisco'
    try:
        idx_repo = cwd.index(nome_repo) + len(nome_repo)
    except ValueError:
        nome_repo = '/1/s'
        idx_repo = cwd.index(nome_repo) + len(nome_repo)
    root_repo = cwd[:idx_repo]

    if cwd == root_repo:
        # sucesso, não precisa alterar o pathIn
        return path

    back_file = '../'
    profundidade_cwd = len(cwd.replace(root_repo, '', 1).split('/')) - 1

    path_ajustado = back_file * profundidade_cwd + path
    return path_ajustado


def get_separator(arquivo):
    '''
    Função que para ler um .csv traduzido de input, pega em separadores.csv qual foi o separador usado para a tradução.
    '''
    path = ajuste_path('data/input/separadores.csv')
    df_sep = pd.read_csv(path, encoding='utf-8')
    arquivo = os.path.splitext(os.path.basename(arquivo))[0]
    df_sep['file'] = df_sep['file'].apply(lambda p: os.path.splitext(p)[0])
    sep = df_sep.loc[df_sep['file'] == arquivo, 'sep']
    if sep.empty:
        raise ValueError("Separator not found in index.")
    result = sep.values[0]
    if result is np.nan:
        return ','
    return result
