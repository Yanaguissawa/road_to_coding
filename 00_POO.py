class Carro:
    def __init__(self, modelo, cor):
        self.modelo = modelo
        self.cor = cor  
        self.velocidade = 0 #o caroo coemca parado

    def acelerar(self,incremento):
        self.velocidade += incremento
        print(f'o carro {self.modelo} acelerou para {self.velocidade} kmhr')

    def desacelerar (self,incremento):
        self.velocidade -= incremento
        print(f'o carro {self.modelo} freiou para {self.velocidade} kmhr')

meu_carro = Carro('Sz Jimmy','verde')

outro_carro = Carro('Fuscao', 'preto')

meu_carro.acelerar(150000)

meu_carro.acelerar(45345345)

outro_carro.desacelerar(600)