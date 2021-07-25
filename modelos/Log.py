
import json

class Log:


    def __init__(self,indice,user,fecha,hashDato,hashBlockchain,motivo):
        self.indice = indice
        self.user = user
        self.fecha = fecha
        self.hashDato=hashDato              #dato realmente no es dato como tal, será un hash generado por el usuario
        self.hashBlockchain=hashBlockchain
        self.motivo=motivo

    def toDict(self):
        return self.__dict__

