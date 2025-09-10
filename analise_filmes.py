from flask import Flask, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
pio.renderers.default = "iframe_connected"  

# alvo
CAMINHO_BANCO = "C:/Users/sabado/Desktop/Lucas PYTHON/filmes.db"

# puxar dados e motnar
def carregar_dados():
    conn = sqlite3.connect(CAMINHO_BANCO)
    df = pd.read_sql_query("SELECT * FROM filmes", conn)
    conn.close()
    return df

# pagina inicial (homepage)
@app.route('/')
def home():
    return '''
        <h1>Dashboard de Filmes</h1>
        <ul>
            <li><a href="/ver_tabela"> Ver Tabela de Filmes</a></li>
            <li><a href="/ver_grafico"> Ver Gráfico de Dispersão</a></li>
            <li><a href="/rota_maneira"> Ver rota maneira</a></li>
        </ul>
    '''

# Rota para mostrar a tabela
@app.route('/ver_tabela')
def ver_tabela():
    df = carregar_dados()
    tabela_html = df.to_html(classes='table table-striped', index=False)
    return render_template_string(f'''
        <h1>Tabela de Filmes</h1>
        {tabela_html}
        <p><a href="/">Voltar</a></p>
    ''')

# Rota para exibir o gráfico
@app.route('/ver_grafico')
def ver_grafico():
    df = carregar_dados()
    df = df.dropna(subset=["Nota"].copy())
    df["Nota_arred"] = df["Nota"].round(1)

    #contar quantos filme por nota
    base = (
        df.groupby("Nota_arred", as_index = "False").agg(Qtd = ("Titulo", "count")).sort_values("Nota_arred")

    )

    if base.empty:
        return render_template_string("<h2>Sem dados de notas para plotar</h2>")

    fig = px.scatter(

        base,
        x = "Nota_arred",
        y = "Qtd",
        title = "Quantidade de filmes por Nota",
        size = "Qtd",
        labels = {
            "Nota_arred":"Nota",
            "Qdt": "Quantidade de filmes"
        }, #nao esqeucer dessa virugla
        hoover_data = 
            ["Nota_arred","Qtd"]
    )
    grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    html = """
            <h1>Grafico</h1>
            <Div>{{grafico|safe}}</Div>
            <br>
        """
    return render_template_string(html, grafico = grafico_html)

@app.route('/rota_maneira')
def rota_maneira():
    df = carregar_dados()

    # fiemes por diretor
    base = (
        df['Direção']
        .value_counts()
        .reset_index()
    )

    # fazer grafico
    fig = px.bar(
        base,
        x='count',
        y='Direção',
        title='Quantidade de filmes por Direção',
        #template = "Plotly_dark" ,
        labels={
            'Direção': 'Direção',
            'Qtd': 'Quantidade de filmes'
        },
    )

    grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    # Basic HTML for rendering
    html = """
        <h1>Gráfico: Filmes por Diretor</h1>
        <div>{{ grafico|safe }}</div>
        <br>
    """

    return render_template_string(html, grafico=grafico_html)


# Executar o app
if __name__ == '__main__':
    app.run(debug=True)
