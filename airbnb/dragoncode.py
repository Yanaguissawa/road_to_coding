import pandas as pd
import numpy as np
import plotly.graph_objs as go

folder = 'C:/Users/sabado/Desktop/Lucas PYTHON/airbnb/'
t_ny = 'ny.csv'
t_rj = 'rj.csv'

def standartize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df =  df.copy()

    lat_candidates = ['lat','latitude','Latitude','LAT','Lat', 'LATITUDE']
    lon_cadidates = ['lon','LON','Lon','Longitude','LONGITUDE','Long','Lng']
    cost_candidates = ['custo','valor','coust','cost','price','preco']
    name_candidates = ['nome','name','titulo','title','local','place','descricao']

    def pick(colnames, candidates):
        #colnames: list de nomes da cokuna da tabela
        #candidates: lista de possiveis nomes das colunas a serem encontrados
        
        #percorra cada candidato (c) dentro da lista de candidatos
        for c in candidates:
            if c in colnames: # se o candidato for exatamente igual a um dos nomes em colnames (tabela)
                return c #retorna o candidato imediatamente
        
        #se nao encontrou a correspondencia percorre novamente cada coluna
        for c in candidates:
            for col in colnames: #aqui percorre cada nome da coluna
                if c.lower() in col.lower(): # faz igual o de cime, mas trabalhando com minusculas
                    return col #retorn a coluna imediatamente
        return None
        #se nao encontrou nenhuma coluna, nem exato nem parcial, retorna non(nenhum match)

    lat_col = pick(df.columns, lat_candidates) 
    lon_col = pick(df.columns, lon_cadidates)
    cost_col = pick(df.columns, cost_candidates)
    name_col = pick(df.columns, name_candidates)
    
    if lat_col is None or lon_col is None:
        raise ValueError (f"nao encontrei a latitude e lingitue: {list(df.columns)}")
    
    out = pd.DataFrame()
    out['lat']      =   pd.to_numeric(df[lat_col], errors ='coerce')
    out['lon']      =   pd.to_numeric(df[lon_col], errors ='coerce')
    out['custo']    =   pd.to_numeric(df[cost_col], errors ='coerce')
    out['nome']     =   pd.to_numeric(df[name_col], errors ='coerce')

    #remove as linhas sem coordenadas

    out = out.dropna(subset=['lat','lon']).reset_index(drop=True)

    #preenche o custo se for ausente
    if out['custo'].notna().any():
        med = float(out['custo'].median())
        if not np.isfinite(med):
            med = 1.0
        out['custo'] = out['custo'].fillna(med)
    else:
        out['custo'] = 1.0
    return out

def city_center(df: pd.DataFrame) -> dict:
    '''
        define funcao citicenter que encontra a latitude e a longitude media de um grande volume de dados
        recebe como parametro um dataframe pandas
        deve retornar um dicionario (-> dict)
    '''
    return dict(
        lat = float(df['lat'].mean()),
        lon = float(df['lon'].mean())
    )

#-------------------- TARCES---------------------

def make_point_trace(df: pd.DataFrame, name:str) -> go.Scattermapbox:
    hover = (
        "<b>%{customdata[0]}</b><br>"
        "Custo: %{customdata[1]}</b><br>"
        "Lat:%{lat:.5f}<br>" 
        "Lon:%{lon:.5f}"
    )
    #tamanho dos marcadores (normalizados pelo custo)
    c = df['custo'].astype(float).values
    c_min, c_max = float(np.min(c)), float(np.max(c))

    #CASO ESPECIAL: Se nao existirem valores numericos validos 
    # ou se todos os custos forem praticamente iguais(diferença) cria um array de tamaho variavel
    if not np.isfinite(c_min) or not np.isfinite(c_max) or abs(c_max - c_min) < 1e-9:
        size = np.full_like(c,10.0, dtype=float)
    
    else: #caso normal: normalizar os custos para um intervalo [0,1] e a escala pode variar entre 6 e 26
        size = (c - c_min) / (c_max - c_min) * 20 + 6

    #mesmo que os dados estejam fora da faixa de 6 a 26 ele evita 
    # sua apresentacao, forcando a ficar entre o itnervalo
    sizes = np.clip(size, 6,26)
    custom = np.stack([df['nome'].values, df['custo'].values], axis=1)    # axis 1 empilha as colunas lado a lado

    return go.Scattermapbox(
        lat = df['lat'],
        lon = df['lon'],
        mode = 'markers',
        marker = dict(
            size = sizes,
            color = df['custo'],
            colorscale = "Viridis",
            colorbar = dict(title='custo')
        ),
        name = f'{name}',
        hovertemplate= hover,
        customdata= custom
    )


def make_density_trace(df: pd.DataFrame, name: str) -> go.Densitymapbox:
    return go.Densitymapbox(
        lat = df['lat'],
        lon = df['lon'],
        z = df['custo'],
        radius = 20,
        colorscale= "Inferno",
        name = f'{name}',
        showscale= True,
        colorbar= dict(title='custo')
    )

#------------- MAIN ----------------
def main():
    #carregando os dados e padronizando
    ny = standartize_columns(pd.read_csv(f'{folder}{t_ny}'))
    rj = standartize_columns(pd.read_csv(f'{folder}{t_rj}'))

    #cria os quatro traces (NY pontos e calor, RJ e pontos e calor)

    ny_point = make_point_trace(ny, 'Nova York')
    ny_heat = make_density_trace(ny, 'Nova York')

    rj_point = make_point_trace(rj, 'Rio de Janeiro')
    rj_heat = make_density_trace(rj, 'Rio de Janeiro')

    fig = go.Figure([ny_point, ny_heat, rj_point, rj_heat])

    def center_zoom(df, zoom):
        return dict(
            center = city_center(df), 
            zoom = zoom
        )
    buttons = [
        dict(
            label = 'nova york potnos',
            method = "update",
            args = [
                {'visible':[True,False, False, False]},
                {'mapbox': center_zoom(ny,9)}
            ]
        ),
        dict(
            label = 'nova york calor',  
            method = "update",
            args = [
                {'visible':[False,True, False, False]},
                {'mapbox': center_zoom(ny,9)}
            ]
        ),
        dict(
            label = 'rio de janeiro pontos',
            method = "update",
            args = [
                {'visible':[False, False, True, False]},
                {'mapbox': center_zoom(rj,10)}
            ]
        ),
        dict(
            label = 'rio de janeiro calor',
            method = "update",
            args =  [
                {'visible':[False, False, False, True]},
                {'mapbox': center_zoom(rj,10)}
            ]     
        )
        ]

    fig.update_layout(
            title='mapa interativo de custos ○ pontos e mapa de calor',
            mapbox_style = "open-street-map", #satellite-streets
            mapbox = dict(center=city_center(rj), zoom=10),
            margin = dict(l=10, r=10, t=50, b=10),
            updatemenus = [dict(
                buttons = buttons, 
                direction = 'down',
                x =0.01,
                y= 0.99,
                xanchor = 'left',
                yanchor = 'top',
                bgcolor = 'white',
                bordercolor = 'lightgrey'
            )],
            legend =  dict(
                orientation = 'h',
                yanchor = 'bottom',
                xanchor = 'right',
                y = 0.01,
                x = 0.99,
            )            
        )

    fig.write_html(f'{folder}mapa_interativos.html', full_html = True, include_plotlyjs = 'cdn')
    print(f'Arquivo gerado com sucesso! \n Salvo em:{folder} mapa_interativos.html')

#inicia o servidor
if __name__ == '__main__':
    main()