import os

import pandas as pd

from .resolve_dir import ajuste_path, get_separator


class WrongFileExtensionError(Exception):
    """
    Classe de erro para o caso onde o arquivo usa a extensão errada.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"WrongFileExtensionError: {self.message}"


def read_input(input_file):
    '''
    Função que lê um csv de input recebendo como entrada apenas o path relativo ao root do arquivo desejado.
    Só funciona para arquivos que estejam na pasta data/input/ deste repsitório
    '''
    nome, extensao = os.path.splitext(input_file)
    if extensao != '.csv':
        raise WrongFileExtensionError(
            message=f'File {input_file} does not use the supported extension. Only .csv files are supported and automatically translated.\n')
    path = ajuste_path('data/input/')
    df = pd.read_csv(path + input_file, sep=get_separator(
        input_file), encoding='utf-8')

    return df
