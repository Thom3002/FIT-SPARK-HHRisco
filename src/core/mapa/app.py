from flask import Flask, render_template, request
from utils_map import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/atualizar_mapa')
def atualizar_mapa_route():
    return atualizar_mapa()


if __name__ == '__main__':
    app.run(debug=True)
