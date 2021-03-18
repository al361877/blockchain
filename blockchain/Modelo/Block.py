from hashlib import sha256
import json

class Block:

    #atributo donde luego almacenaré el hash
    hash=None

    def __init__(self,indice,datos,fecha,prev_hash ):
        self.indice=indice
        self.datos=datos
        self.fecha=fecha
        self.prev_hash =prev_hash

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
