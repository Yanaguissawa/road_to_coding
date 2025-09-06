#      _                                __       _                              
#     | | ___  ___ _   _  ___   _ __   /_/    __| | ___    ___ __ _ _ __   __ _ 
#  _  | |/ _ \/ __| | | |/ _ \ | '_ \ / _ \  / _` |/ _ \  / __/ _` | '_ \ / _` |
# | |_| | (_) \__ \ |_| |  __/ | |_) |  __/ | (_| |  __/ | (_| (_| | | | | (_| |
#  \___/ \___/|___/\__,_|\___| | .__/ \___|  \__,_|\___|  \___\__,_|_| |_|\__,_|
#                              |_|                                              

#Author: Lucas Yanaguissawa
#versao 0.0.1v 09-2025
#CAMINH DA PASTA
DB_PATH = "C:/Users/noturno/Desktop/road_to_coding-main/"
NOMEBANCO = "bancoDeElite.db"
TABELA_A = 'drinks.csv'
TABELA_B = 'avengers.csv'

#definicoes do servidor
FLASK_DEBUG = True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

#rotas (caminhos de cada pagina)
ROTAS = [
    '/',                #rota00
    '/grafico1',        #rota01
    '/grafico2',        #rota02
    '/grafico3',        #rota03
    '/grafico4',        #rota04
    '/comparar',        #rota05
    '/upload',          #rota06
    '/apagar',          #rota07
    '/ver',             #rota08
    '/final'            #rota09
]

#---------------------------------------
#           Consultas SQL           
#---------------------------------------

