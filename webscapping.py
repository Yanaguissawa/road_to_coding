import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3
import datetime

#headers para simular que somo um nevagador real

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
baseURL = "https://www.adorocinema.com/filmes/melhores/"
filmes = [] #lista que vai armazenar os dados dos filmexs
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
inicio = datetime.datetime.now()

card_temp_min = 1
card_temp_max = 3
pag_temp_min = 2
pag_temp_max = 4
paginaLimite = 2 #limite de paginas a serem scaneadas
bancoDados = 'filmes.db'
saidaCSV = f'filmes_{data_hoje}.csv'

for pagina in range(1, paginaLimite + 1):
    url = f'{baseURL}?page={pagina}'
    print(f'Coletando dados da pagina {pagina} \n URL: {url}')
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code != 200:
        print(f'Erro ao acessar a pagina {pagina}. Status code: {resposta.status_code}')
    soup = BeautifulSoup(resposta.text, "html.parser")

    cards = soup.find_all("div", class_= "card entity-card entity-card-list cf")

    for card in cards:
        try:
            #captura o titulo do filme e o hiperlink da pagina do filme
            titulo_tag = card.find("a", class_ = "meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com/" + titulo_tag['href'] if titulo_tag else None

            nota_tag = card.find("span", class_ = "stareval-note")
            nota = nota_tag.text.strip().replace(',','.') if nota_tag else "N/A"

            diretor = "N/A"
            genero_block = None     

            #caso exsite um link, acessar a pagina individual do filme e capturar os dados.

            if link:
                filme_resposta = requests.get(link, headers=headers)
                if filme_resposta.status_code == 200:
                    filme_soup = BeautifulSoup(filme_resposta.text, "html.parser")
                    
                    #bora capturar o diretor
                    diretor_tag =  filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-oneline")
                    if diretor_tag:
                        diretor = (
                            diretor_tag.text
                            .strip()
                            .replace('Direção:','')
                            .replace(',','')
                            .replace('|','')
                            .replace('\n',' ')
                            .replace('\r','')
                            .strip()
                                )
                    #capturar os generos (fallback se nao acessou o link)
                    genero_block = filme_soup.find('div', class_='meta-body-info')
                    if genero_block:
                        genero_links = genero_block.find_all('a')
                        generos = [g.text.strip() for g in genero_links]
                        categoria = ", ".join(generos[:3] if generos else "N/A")
                    else:
                        categoria = "N/A"

                    #captura do ano de lancamento do filme
                    #dica: a tag span e o noma da classe é date
                    ano_tag = genero_block.find('span', class_= 'date') if genero_block else None
                    ano = ano_tag.text.strip() if ano_tag else "N/A"

                    #so adiciona o filme se todos os dados princiapis existirem
                    if titulo != "N/A" and link is not None and nota != "N/A":
                        filmes.append({
                            "Titulo":titulo,
                            "Direção":diretor,
                            "Nota":nota,
                            "Link":link,
                            "Ano":ano,
                            "Categoria": categoria
                        })
                    else:
                        print(f'Filme incompleto ou erro na coleta de dados {titulo}')
                    
                    #aguardar um tempo aleatorio para nao sobrecarregar o site
                    tempo = random.uniform(card_temp_min,card_temp_max)
                    print(f'Tempo de espera entre cartoes: {tempo:.1f}s')
                    time.sleep(tempo)
        except Exception as erro:
            print(f' erro ao processar o filme {titulo} - Erro: {erro}')
    
    tempo = random.uniform(pag_temp_min,pag_temp_max)
    print(f'Tempo de espera entre paginas : {tempo:.1f}s')
    time.sleep(tempo)

#converter os dados em um df do pandas
df = pd.DataFrame(filmes)
print(df.head())

#vamos salvar os dados e o arquivo csv
df.to_csv(saidaCSV)

df.to_csv(saidaCSV, index=False, encoding='utf-8-sig', quotechar="'", quoting=1)

#conectar
conn = sqlite3.connect(bancoDados)
cursor = conn.cursor()
#tabela simples: link unico para evitar repeticao ao rodar de novo (idempotente)
cursor.execute('''
               CREATE A TABLE IF NOT EXISTS filmes(
                    if  
                        id INTEGER PRIMARY KEY AUTOINCREMENT
                        Titulo TEXT
                        Direcao TEXT
                        Nota REAL,
                        Link TEXT UNIQUE,
                        Ano TEXT,
                        Categoria TEXT,
               )
                ''')

#INSERIR CADA FILME COLETADO
for filme in filmes:
    try:
        cursor.execute('''
            INSERT OR IGNOREN INTO filmes (Titulo, Direcao, Nota, Link, Ano, Categoria) VALUES (?,?,?,?,?,?)
                       ''',(
                    filme['Titulo'],
                    filme['Direção'],
                    filme[filme['Nota']] if filme['Nota'] != 'N/A' else None,
                    filme['Link'],
                    filme['Ano'],
                    filme['Categoria'],
        ))
    except Exception as erro:


print("Dados raspados e salvo com sucesso")
print(f"\n Arquvo salvo em saida CVS")
print("\nObrigado por usar o sistema de bot cinemao stud G")
print(f"\n Iniciado em {inicio.strftime("%d-%m-%Y")}")
print("----------------------------------------------------------------")