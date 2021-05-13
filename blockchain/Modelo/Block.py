from hashlib import sha256
import json
import random
from pprint import pprint

from blockchain.Modelo.Transaccion import Transaccion


class Block:

    #las transacciones serán objetos, para poder cifrarlos, pero para almacenarlos en el diccionarió, solo serán una tupla con 2 datos, la fecha y el dato


    def __init__(self):
        #atributo donde luego almacenaré el hash
        self._id=None                           #he cambiado la palabra hash, por _id, para poderlo almacenar en mongodb con el hash como id, en vez de que me cree el uno propio
        self.indice=0
        self.transacciones={}                   #transacciones es un diccionario cuya clave es el hashBlockchain y el valor es una tupla hashDato

        self.prev_hash="apunto al anterior"
        self.Nonce=0                            #atributo para que un bloque con los mismos datos genere un hash distinto
        self.MAX_TRANS=10                       #numero maximo de transacciones por bloque
        self.trabajo='abc'

        #self.maquina=? #aqui ira guardado desde que maquina se ha realizado el bloque

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=False)
        resultado=sha256(block_string.encode()).hexdigest()
        return resultado

    #lo mina este bloque, pero luego puede que se guarde en otro, porque se haya cerrado antes el programa
    def add_transaccion(self,hashDato):
        transaccion=Transaccion(hashDato)

        hashT=transaccion.compute_hash()

        #prueba de trabajo
        while(not hashT.startswith(self.trabajo)):
            transaccion.Nonce+=1
            hashT=transaccion.compute_hash()


        #le doy valor al hash, que hasta ahora no tenia valor
        transaccion.hash=hashT

        #es la tupla que voy a almacenar en el bloque
        trans=transaccion.hashDato
        self.transacciones[hashT]=trans

        return transaccion

    def add_transaccion_minada(self,transaccion):

        self.transacciones[transaccion["_id"]]=transaccion["hashDato"]

    def set_hash(self,hash):
        self._id=hash

    def get_hash(self):
        return self._id

    def get_prev_hash(self):
        return self.prev_hash

    def get_indice(self):

        return self.indice


    #si el bloque ya esta completo devolvera true, si no devolvera false
    def completo(self):

        return len(self.transacciones)>=self.MAX_TRANS

    def get_transacciones(self):
        return self.transacciones

    def toString(self):
        return json.dumps(self.__dict__,sort_keys=False)
