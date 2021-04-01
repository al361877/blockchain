import json
from hashlib import sha256


class Transaccion:

    hash=None
    Nonce=0

    def __init__(self,dato,fecha):
        self.dato=dato
        self.fecha=fecha

    def compute_hash(self):
         transaccion_string = json.dumps(self.__dict__, sort_keys=True)
         resultado= sha256(transaccion_string.encode()).hexdigest()
         return resultado

