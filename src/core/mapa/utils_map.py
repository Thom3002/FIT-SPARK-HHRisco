import os

import folium
import numpy as np
import pandas as pd
import requests as req
from branca.element import MacroElement
from flask import Flask, render_template, request
from folium.plugins import Fullscreen
from jinja2 import Template
from resolve_path import ajuste_path

corMaisFraca = "#dfc27d"
corMediaFraca = "#bf812d"
corMediaForte = "#8c510a"
corMaisForte = "#543105"

cores_intermediarias_gradiente = [
    corMaisFraca, corMediaFraca, corMediaForte, corMaisForte]

# Define a classe Legend (Para que a legenda não desapareça no modo fullscreen)


class Legend(MacroElement):
    def __init__(self, legend_html, marginright, position='bottomright'):
        super(Legend, self).__init__()
        self._name = 'Legend'
        self.legend_html = legend_html
        self.position = position
        self.marginright = marginright
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            L.Control.Legend = L.Control.extend({
                onAdd: function(map) {
                    var div = L.DomUtil.create('div', 'legend-control');  // Assign class here
                    div.innerHTML = `{{this.legend_html}}`;
                    div.style.marginRight = '{{this.marginright}}';
                    return div;
                },
                onRemove: function(map) {
                    // Nothing to do here
                }
            });
            L.control.legend = function(opts) {
                return new L.Control.Legend(opts);
            }
            L.control.legend({ position: '{{this.position}}' }).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """)


def get_color_discrete(probabilidade):
    if probabilidade is np.nan:
        return "#000000"
    elif probabilidade < 0.25:
        return corMaisFraca
    elif probabilidade < 0.5:
        return corMediaFraca
    elif probabilidade < 0.75:
        return corMediaForte
    else:
        return corMaisForte


def get_font_color(marker_color):
    """Define a cor da probabilidade de acordo com a cor do marcador."""
    if marker_color in [corMaisForte, corMediaForte]:
        return corMaisFraca
    elif marker_color == corMaisFraca:
        return corMediaForte
    return corMaisForte


def criar_popup(row):
    """Cria o conteúdo HTML do popup."""
    return f"""
        <div>
            <div style="font-size: 1.1em;">
                <b>Local:</b> {row['local_de_instalacao']}<br>
            </div>
            <div style="margin-top: 10px;">
                <b>HH total por mês em {row['mes']}/{row['ano']}:</b> {round(row['hh_total'], 2)}<br>
                <b>Probabilidade:</b> {round(row['probabilidade'], 2)}
            </div>
        </div>
    """


def criar_html_marcador(row, color, font_color):
    """Cria o HTML do marcador com base no tipo de local de instalação."""
    base_style = """
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        position: relative;
        cursor: pointer;
        transition: transform 0.3s ease;
    """
    hover_effect = "onmouseover=\"this.style.transform='scale(1.2)'\" onmouseout=\"this.style.transform='scale(1)'\""
    content_style = f"""
        background-color: {font_color};
        color: {font_color};
        width: 35px;
        height: 35px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 8px;
        font-weight: bold;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    """
    shape_interno = f"""
            width: 94%;
            height: 94%;
            background-color: {color};
            justify-content: center;
            align-items: center;
        """
    if row['local_de_instalacao'].startswith('S-L'):  # Linha de transmissão (losango)
        shape = "clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);"
        class_name = "map-marker vao"
    elif row['local_de_instalacao'].startswith('S-U'):  # Usina (trapézio)
        shape = "clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);"
        class_name = "map-marker usina"
    else:  # Subestação (círculo)
        shape = "border-radius: 50%;"
        class_name = "map-marker subestacao"

    return f"""
        <div class={class_name} data-local="{row['local_de_instalacao']}" style="{base_style}" {hover_effect}>
            <div style="{content_style} {shape}">
                <div style="{content_style} {shape} {shape_interno}">
                {round(row['probabilidade'] * 100)}%
                </div>
            </div>
        </div>
    """


def filtra_df_por_tempo(df, mes, ano):
    """Função que define o período de tempo para a visualização do mapa"""
    df = df.query("`mes` == @mes and `ano` == @ano")
    return df

# Função para adicionar um marcador com o acidente ao mapa


def adiciona_acidente(mapa, row, color):

    popup_content = (
        f"<b>Local Associado:</b> <span>{row['local_de_instalacao']}</span><br>"
        f"<b>ID do Funcionário:</b> <span>{row['no_pessoal']}</span><br>"
        f"<b>Classificação:</b> <span>{row['classificacao_acidente']}</span><br>"
        f"<b>Mes do Acidente:</b> <span>{row['data_acidente']}</span>"
        # f"<b>Potencial:</b> <span>{row['potencial_acidente']}</span><br>"
    )
    # Ajuste o valor de max_width conforme necessário
    popup = folium.Popup(popup_content, max_width=2650, offset=(5, 0))

    folium.Marker(
        location=[row['latitude_acidente'], row['longitude_acidente']],
        popup=popup,
        rise_on_hover=True,
        zIndexOffset=1,
        tooltip=row['local_de_instalacao'],
        icon=folium.DivIcon(
            html=f"""
            <div class="map-marker acidente" data-local="{row['local_de_instalacao']}" style="
                width: 0;
                height: 0;
                border-left: 12px solid transparent;
                border-right: 12px solid transparent;
                border-bottom: 24px solid {color};
                position: relative;
                cursor: pointer;
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='scale(1.2)'"
            onmouseout="this.style.transform='scale(1)'">
                <div style="
                    position: absolute;
                    top: 5px;
                    left: 50%;
                    transform: translate(-50%, 0);
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                ">
                    !
                </div>
            </div>
            """
        )
    ).add_to(mapa)


def adiciona_camadas(map_object, df, nome_camada):
    camada = folium.FeatureGroup(name=nome_camada)
    for _, row in df.iterrows():
        color = get_color_discrete(row["probabilidade"])
        font_color = get_font_color(color)
        popup_content = criar_popup(row)
        html = criar_html_marcador(row, color, font_color)

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            rise_on_hover=True,
            icon=folium.DivIcon(html=html),
            popup=folium.Popup(popup_content, max_width=2650, offset=(5, -15)),
            zIndexOffset=round(row["probabilidade"] * 100),
            tooltip=row['local_de_instalacao']
        ).add_to(camada)

    map_object.add_child(camada)


def atualizar_mapa():
    mes = int(request.args.get('mes'))
    ano = int(request.args.get('ano'))

    # Carrega os datasets
    pathUtil = ajuste_path('data/util/')
    df_mapa = pd.read_csv(os.path.join(pathUtil, 'dataset_mapa.csv'), sep=',')

    # Remover as linhas onde as colunas 'latitude' ou 'longitude' estejam NaN
    df_mapa = df_mapa.dropna(subset=['latitude', 'longitude'])

    # Filtra o df_mapa com os valores da data especificada
    df_mapa_max_prob = df_mapa.loc[df_mapa.groupby(
        ['ano', 'mes', 'local_de_instalacao'])['probabilidade'].idxmax()]

    df_filtrado = filtra_df_por_tempo(df_mapa_max_prob, mes, ano)

    # Cria o mapa
    media_x = df_filtrado["latitude"].mean()
    media_y = df_filtrado["longitude"].mean()
    mapa = folium.Map(
        location=[media_x, media_y],
        zoom_start=5,
        control_scale=True,
        dragging=True,
        max_zoom=18,
        min_zoom=4,
    )

    # Adiciona o botão de fullscreen
    Fullscreen(position='topright', force_separate_button=True).add_to(mapa)

    # Adiciona legenda
    caminho_legenda_html = ajuste_path(
        'src/core/mapa/static/assets/legenda.html')
    with open(caminho_legenda_html, "r", encoding="utf-8") as arquivo:
        legenda_html = arquivo.read()

    legend = Legend(legend_html=legenda_html,
                    marginright='5.6vw', position='bottomright')
    mapa.add_child(legend)

    # Adicionar a camada de polígonos de estados do Brasil
    url_poly_brasil = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=UF"

    headers = {"Accept": "application/vnd.geo+json"}

    mapa_brasil = req.get(url_poly_brasil, headers=headers)

    poly_brasil = mapa_brasil.json()
    camada_poligonos_brasil = folium.FeatureGroup(name="Polígonos do Brasil")
    folium.GeoJson(
        poly_brasil,
        zoom_on_click=True,
        style_function=lambda feature: {
            "fillColor": "#c8d977",
            "color": "#A9A9A9",
            "weight": 2,
            "dashArray": "5, 5",
            "fillOpacity": 0.15,
        },
    ).add_to(camada_poligonos_brasil)
    mapa.add_child(camada_poligonos_brasil)

    # Filtra o df_mapa somente com os valores de probabilidade máxima para cada local, ano e mês.
    df_mapa_max_prob = df_mapa.loc[df_mapa.groupby(
        ['ano', 'mes', 'local_de_instalacao'])['probabilidade'].idxmax()]

    # Adiciona camada ao mapa
    adiciona_camadas(mapa, df_filtrado, f"Exibir probabilidade de {mes}/{ano}")

    # Filtrar o DataFrame para remover linhas com valores NaN nas colunas de latitude e longitude
    df_acidentes = df_mapa.dropna(
        subset=['latitude_acidente', 'longitude_acidente'])

    # Filtra o df_acidentes para o mês e ano especificados
    df_acidentes = filtra_df_por_tempo(df_acidentes, mes, ano)

    # Adicionar marcadores ao mapa para os acidentes
    for _, row in df_acidentes.iterrows():
        if row['classificacao_acidente'] == 'fatalidade':
            color = '#000000'
        elif row['potencial_acidente'] <= 8:
            color = '#d7301f'
        elif row['potencial_acidente'] <= 12:
            color = '#fec44f'
        else:
            color = '#006d2c'
        adiciona_acidente(mapa, row, color)
    # Retorna o HTML do mapa
    return mapa._repr_html_()
