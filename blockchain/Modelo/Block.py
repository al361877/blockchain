from hashlib import sha256
import json
import random

class Block:

    #atributo donde luego almacenaré el hash
    hash=None
    indice=0
    datos="genesis"
    fecha="fecha"
    prev_hash="apunto al anterior"
    token=None
    aleatorio=0 #atributo para que un bloque con los mismos datos genere un hash distinto

    def __init__(self,indice,datos,fecha,prev_hash ,token):
        self.indice=indice
        self.datos=datos
        self.fecha=fecha
        self.prev_hash =prev_hash
        self.token=token

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        resultado=sha256(block_string.encode()).hexdigest()
        return resultado

    def set_hash(self,hash):
        self.hash=hash

    def get_hash(self):
        return self.hash

    def get_prev_hash(self):
        return self.prev_hash

    def get_indice(self):
        return self.indice

    def random(self):
        self.aleatorio=random.randint(0,50)

    def get_datos(self):
        return self.datos

    def get_token(self):
        return self.token
