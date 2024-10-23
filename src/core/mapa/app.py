# Arquivo de configuração das rotas da aplicação web que contém o mapa
from flask import Flask, render_template
from utils_map import *

app = Flask(__name__)

# Rota principal da aplicação, renderiza o 'index.html' que contém o mapa


@app.route('/')
def index():
    return render_template('index.html')


# Rota que atualiza o mapa se o botão 'Atualizar Mapa' do filtro de seleção de data for clicado
@app.route('/atualizar_mapa')
def atualizar_mapa_route():
    return atualizar_mapa()


if __name__ == '__main__':
    app.run(debug=True)
