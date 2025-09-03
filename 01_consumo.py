from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3 
import plotly.express as px
import plotly.io as pio
import random
import config_PythonsDeElite as config
import consultas

caminhoBanco = config.DB_PATH
pio.renderers.default = "browser"
nomeBanco = config.NOMEBANCO
rotas = config.ROTAS
tabelaA = config.TABELA_A
tabelaB = config.TABELA_B


#arquivos a serem carregados
dfDrinks = pd.read_csv(f'{caminhoBanco}{tabelaA}')
dfAvengers = pd.read_csv(f'{caminhoBanco}{tabelaB}', encoding='latin1')

#outros exemplos: utf-8, tf-16, cp1256, iso8859-1

#criamos o banco de dados em sql caso nao exista
conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}]')

dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)

dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

html_template = f'''
    <h1>Dashboards</h1>
    <h2>Parte 01</h2>
    <ul>
        <li>    <a href="{rotas[1]}">Top 10 paises em consumo XOMPS </a>    </li>
        <li>    <a href="{rotas[2]}">media de consumo por tipo </a>    </li>
        <li>    <a href="{rotas[3]}">Consumo por regiao </a>    </li>
        <li>    <a href="{rotas[4]}">Comparativo entre tipos </a>    </li>
    </ul>
    <h2>parte 02</h2>
    <ul>
        <li>    <a href="{rotas[5]}">Comparar </a>    </li>
        <li>    <a href="{rotas[6]}">Upload </a>    </li>
        <li>    <a href="{rotas[7]}">Apagar tabela </a>    </li>
        <li>    <a href="{rotas[8]}">Ver tabela </a>    </li>
        <li>    <a href="{rotas[9]}">V.A.A </a>    </li>
    </ul>
'''

#inicia o flask
app = Flask(__name__)

@app.route(rotas[0])
def index():
    return render_template_string(html_template)

@app.route(rotas[1])
def grafico1():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta01, conn)
    figuraGrafico1 = px.bar(
        df, 
        x = 'country',
        y = 'total_litres_of_pure_alcohol',
        title = 'top 10 paises em consumo de alcool'
    )
    return figuraGrafico1.to_html()

@app.route(rotas[2])
def grafico1():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta01, conn)
    figuraGrafico1 = px.bar(
        df, 
        x = 'country',
        y = 'total_litres_of_pure_alcohol',
        title = 'top 10 paises em consumo de alcool'
    )
    return figuraGrafico1.to_html()


#inicia o servidor
if __name__ == "__main__":
    app.run(debug=True)









