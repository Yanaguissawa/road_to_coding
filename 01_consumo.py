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

def getDBConnect():
    conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
    conn.row_factory = sqlite3.Row
    return conn


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
def grafico2():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta02, conn)
#transforma as colunas cerveja destilados e vinhos e  linhas criando no fim duas colunas,
#uma chamada bebibas com os nomes originais das colunas e outra com a media das procoes com seus valores correspondentes.
        df_melted = df.melt(var_name='bebidas', value_name= 'media de porcoes')
        figuraGrafico2 = px.bar(
            df_melted,
            x = 'bebidas',
            y = 'media de porcoes',
            title = 'media de consumo global por tipo'
        )
        return figuraGrafico2.to_html()

@app.route(rotas[3])
def grafico3():
    regioes = {
        "Europa": ['France','Germany','Spain','Italy','Portugal'],
        "Asia" : ['China','Japan','India','Thailand'],
        "Africa": ['Angola','Nigeria','Egypt','Algeria'],
        "Americas": ['USA','Brazil','Canada','Argentina','Mexico']
    }
    dados = []
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        #itera sobre o dicionario de regioes onde cada chave (regiao tem uma lista de pasies)
        for regiao, paises in regioes.items():
            #criando a lista de placeholders para os paises dessa regiao
            #isso vai ser usado na consulta sql para filtrar o pais da regiao
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f"""
                SELECT SUM(total_litres_of_pure_alcohol) AS total
                FROM bebidas
                WHERE country IN ({placeholders})
            """
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append(
                {
                    "Regiao": regiao,
                    "Consumo Total": total
                }

                )
    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,  
        names= "Regiao",
        values="Consumo Total",
        title="Consumo total por regiao",
    )
    return figuraGrafico3.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"

@app.route(rotas[4])
def grafico4():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(consultas.consulta03, conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo', 'Media']
        figuraGrafico4 = px.pie(
            medias,
            names="Tipo",
            values="Media",
            title="Proprocao media entre os tipos de bebidas"
        )
    return figuraGrafico4.to_html() + f"<br><a href='{rotas[0]}'>Voltar</a>"

@app.route(rotas[5], methods= ["POST", "GET"])
def comparar():
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]

    if request.method == "POST":
        eixo_X = request.form.get('eixo_x')
        eixo_Y = request.form.get('eixo_y')
        if eixo_X == eixo_Y:
            return f"<h3> Selecione campos diferentes! <h3> <br><a href='{rotas[0]}'>Voltar</a>"
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixo_X, eixo_Y), conn)
        conn.close()
        figuraComparar = px.scatter(
            df,
            x =eixo_X,
            y = eixo_Y,
            title = f"Comparacao entre {eixo_X} e {eixo_Y}"
        )
        figuraComparar.update_traces(textposition = 'top center')
        return figuraComparar.to_html()  + f"<br><a href='{rotas[0]}'>Voltar</a>"

    return render_template_string('''
        <h2>Comparar campos </h2>
        <form method="POST">
              <label>Eixo X: </label>
                <select name="eixo_x">
                    {% for opcao in opcoes %}
                           <option value='{{opcao}}'>{{opcao}}</option>
                    {% endfor %}                    
                </select>
            <br><br>                      
              <label>Eixo Y: </label>
                <select name="eixo_y">
                    {% for opcao in opcoes %}
                           <option value='{{opcao}}'>{{opcao}}</option>
                    {% endfor %}             
                </select>    
            <br><br>
                <input type="Submit" value="---Comparar---">                      
        </form>
        <br><a href="">Voltar</a>
    ''', opcoes = opcoes, rotaInterna = rotas[0])


@app.route(rotas[6], methods= ["POST", "GET"])
def upload():

    if request.method == "POST":
        recebido = request.files['c_arquivo']
        if not recebido:
            return f"<h3> nenhum arquivo enviado! </h3> <br><a href='{rotas[0]}'>Voltar</a>"
        dfAvengers = pd.read_csv(recebido,encoding='latin1')
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close() 
        return f"<h3> upload feito com sucesso </h3> <br> <a href='{rotas[0]}'>Voltar</a>"

    return '''
            <h2> Upload da tabela Avengers </h2>
            <form method="POST" enctype="multipart/form-data">
                <!-- ver essa parte para aceitar excel ou csv -->
                <input type="file" name="c_arquivo" accept=".csv">
                <input type="submit" value = "-- carregar --" >
            </form>


    '''
@app.route('/apagar_tabela/<nome_tabela>/', methods = ['GET'])
def apagarTabela(nome_tabela):
    conn = getDBConnect()
    #realiza o apontamento para o banco que sera manipulado
    cursor = conn.cursor()
    #usaremos o try except para controlar possiveis erros
    #confirmar antes se a tabela existe
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='tabela' AND name='?'", (nome_tabela,))
    #pega o resultado da contagem(0 se nao existir e 1 se existir)
    existe = cursor.fetchone()[0] 
    if not existe :
        conn.close()
        return "Tabela nao encontrada"
    
    try:
        cursor.execute(f' DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f"Tabela {nome_tabela} apagada"

    except Exception as erro:
        conn.close()
        return f"NAO FOI POSSIVEL APAGAR A TABELA: erro {erro}"

@app.route(rotas[8], methods=["POST", "GET"])
def ver_tabela():
    if request.method == "POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3>Tabela {nome_tabela} nao encontrada </h3><br><br> <a href={{rotas [8]}}> Voltar </a>"
        conn = getDBConnect
        df = pd.read_sql_query(f"SELECT * from {nome_tabela}", conn)
        conn.close()

        tabela_html = df.to_html(classes="table table-striped")
        return f'''
            <h3>Conteudo da tabela {nome_tabela}: </h3>
            {tabela_html}
            <br><a href="{rotas[8]}>Voltar</a>
        '''


    return render_template_string('''
        <marquee> Selecione a tabela a ser visualizada </marquee>
        <form method="POST">
        <label>Escolha a tabela abaixo:</label>
        <Select name="tabela">                           
                <option value="" disabled selected>Select an option</option>
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
        </Form>                 
        </Select>
        <hr>
        <input type="Submit" value="Consultar Tabela">
        <br> <a href="{{rotas [0]}}'> Voltar </a>                          
        ''', rotas = rotas)



#inicia o servidor
if __name__ == "__main__":
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
        )









