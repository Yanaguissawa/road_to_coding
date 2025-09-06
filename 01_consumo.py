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

@app.route(rotas[9], methods=['GET', 'POST'])
def vaa_mortes_consumo():
    metricas_beb = {
        "Total (L de Alcool)":"Total_litres_pf_pure_alcohol",
        "Cerveja (Doses)":"beer_servings",
        "Destilados (Doses)":"spirit_servings",
        "Vinho (Doses)":"wine_servings",
    }
    
    
    if request.method == "POST":
        met_beb_key = request.form.get("metrica_beb") or "Total (L de Alcool)"
        met_beb = request.get(met_beb_key, "tal_litres_pf_pure_alcohol")

        #semente opcional para reproduzir a mesma distribuicao de paises nos vingadores
        try:
            semente = int(request.form.get("semente"))
        except:
            semente = 42

        sementeAleatoria = random.Random(semente) #gera o valor aleatorio baseado na semente escolhida

        #le os dados do banco do SQL
        with getDBConnect() as conn:
            dfA = pd.read_sql_query('SELECT * FROM vingadores', conn)
            dfB = pd.read_sql_query('SELECT country, beer_servings, spririt_servings, wine_servings, total_litres_of_pure_alcoholFROM bebidas', conn)

        #------ Mortes dos vingadores
        # estrategia: somar as colunas que contenham o death como true (case insensitive)
        #contaremos nulos como 1, ou seja, death tem True? vale 1 nao em anda vale 0
        death_cols = [c for c in dfA.columns if 'death' in c.lower()]
        if death_cols:
            dfA["Mortes"] = dfA[death_cols].notna().astype(int).sum(axis=1)
        elif "Deaths" in dfA.columns:
            #fallback obvio
            dfA["Mortes"] = pd.to_numeric(dfA["Deaths"], errors="coerse").fillna(0).astype(int)
        else:
            dfA["Mortes"] = 0

        if "Name/Alias" in dfA.columns:
            col_name = "Name/Alias"
        elif "" in dfA.columns:
            col_name = ""
        elif "Alias" in dfA.columns:
            col_name = "Alias"
        else:
            possivel_texto = [c for c in dfA.columns if dfA[c].dtype == "object"]
            col_name = possivel_texto[0] if possivel_texto else dfA.columns[0]
        
        dfA.rename(columns={col_name:"Personagem"}, inplace = True)

        #--------------- definir um pais para cada vingador
        paises = dfB["country"].dropna().astype(str).to_list()
        if not paises:
            return f"<h3> nao ha paises na tabela de bebidas </h3> <a href={rotas[9]}>Voltar</a> "
        
        dfA["Pais"] = [sementeAleatoria(paises) for _ in range(len(dfA))] 
        dfB_const = dfB["country",met_beb].rename(columns={"country":"Pais", met_beb : "Consumo"})
        Base = dfB[["Personagem", "Mortes", "Pais"]].merge(dfB_const, on="Pais", how = "left" )

        #filtrar apenas linhas validas
        base =  base.dropna(subset=["Consumo"])
        base["Mortes"] = pd.to_numeric(base["Mortes"], errors="Coerse").fillna(0).astype(int)
        base = base[base["Mortes"] >= 0]
        #correlacao (se possivel)
        coor_txt = ""
        if base["Consumo"].notna().sum() >= 3 and base["Mortes"].notna().sum >= 3:
            try:
                corr = base["Consumo"].corr(base["Mortes"])
                corr_txt = f" r = {corr:.3f}"

            except Exception:
                pass

        #==================== grafico scatter 2d: consumo x mortes (cor = pais) ==========================
        fig2d = px.scatter(
            base,
            x= "Consumo", 
            y= "Mortes",
            color=" Pais",
            hover_name= "Personagem",
            hover_data = {
                "Pais": True,
                "Consumo": True,
                "Mortes": True
                },
            title = f"vingadores - mortes vs consumo de alcool do pais ({met_beb_key}){corr_txt}"
        )

        fig2d.update_layout(
            xaxis_title = f"{met_beb_key}",
            yaxis_title = "Mortes(contagem)",
            margin = dict(l=40, r=20, t=70, b=40)
        )

        return (
        "<h3> ----Grafico 2d---- </h3>"
        + fig2d.to_html(full_html = False)
        + "<hr>"
        + "<h3> --- grafico 3d---- </h3>"
        + "<p> Em breve </p>"
        + "<hr>"
        + "<h3> ----- Preview dos dados ------ </h3>"
        + "<p> Em breve </p>"
        + "<hr>"
        + f"<a href = {rotas[0]}> Menu Inicial</a>"
        + "<br>"
        + f"<a href = {rotas[9]}> Voltar</a>"
        )

    return render_template_string('''
    <style>
/* Soviet Style - style.css */
body {
    background-color: #2b2b2b; /* industrial grey */
    font-family: "Courier New", Courier, monospace;
    color: #f1f1f1;
    padding: 20px;
}

h2 {
    color: #ff0000;
    text-align: center;
    border-bottom: 2px solid #cc0000;
    padding-bottom: 10px;
    font-size: 26px;
    text-transform: uppercase;
    letter-spacing: 2px;
}

form {
    background-color: #3b3b3b;
    border: 2px solid #990000;
    padding: 20px;
    max-width: 500px;
    margin: auto;
    border-radius: 10px;
    box-shadow: 0 0 10px #cc0000;
}

label {
    display: block;
    margin-top: 15px;
    color: #ffcc00;
    font-weight: bold;
}

select, input[type="number"] {
    width: 100%;
    padding: 10px;
    background-color: #1e1e1e;
    color: #fff;
    border: 1px solid #990000;
    border-radius: 5px;
    margin-top: 5px;
}

input[type="submit"] {
    margin-top: 20px;
    width: 100%;
    background-color: #cc0000;
    color: #fff;
    border: none;
    padding: 12px;
    font-size: 16px;
    cursor: pointer;
    text-transform: uppercase;
    font-weight: bold;
    border-radius: 5px;
}

input[type="submit"]:hover {
    background-color: #ff1a1a;
    box-shadow: 0 0 8px #ff0000;
}

p {
    margin-top: 30px;
    font-style: italic;
    font-size: 14px;
    color: #ccc;
    text-align: center;
}

a {
    display: block;
    text-align: center;
    color: #ffcc00;
    font-weight: bold;
    text-decoration: none;
    margin-top: 20px;
}

a:hover {
    text-decoration: underline;
    color: #ffff66;
}


    </style>                         
        
    <h2> VAAA - Pais x consumo x mortes </h2>
    <form method="POST">
        <label for="metrica_beb"> <b> metrica de consumo <b> </label>
        <select name ="metrica_beb" id="metrica_beb">                              
                    {% for doses in metricas_beb.keys() %}
                           <option value="{{doses}}">{{doses}}</option>
                    {% endfor %}  
        </select>
        <br><br>
        <label for="Semente"> <b>Semente:</b> (<i>opcional, p/reprodutibilidade<i>) </label>
        <input type="number" name="semente" id="semente" value="42">
        
        <br><br>
        <input type="submit" value=" ---- Gerar Pickles -----"> </input>                          
    </form>
    <p>
        esta visao sortei um pais para cada vingador, soma as mortes dos personagens e  anexa o consumo de alcool do pais, ao fim, plota um scatter 2d e um grafico 3d                          
    </p>
                                  <br>

    <a href={{rotas[0]}}> Voltas </a>
''', metricas_beb = metricas_beb, rotas=rotas)



#inicia o servidor
if __name__ == "__main__":
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
        )









