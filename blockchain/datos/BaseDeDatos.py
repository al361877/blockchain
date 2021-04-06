import json
from pprint import pprint

import pymongo

from pymongo import MongoClient


myclient = pymongo.MongoClient('mongodb://localhost:27017/')

db=myclient['blockchain']
col=db['bloques']

def almacenarBloque(bloque):
    dato=json.dumps(bloque.__dict__)
    print(dato)
def almacenarBlockchain(lista):

    for elemento in lista:
        dato=elemento.__dict__
        x=col.insert(dato)
        print(x)
def consultaDatos():
    for x in col.find():
        print(x)
def consultaUnaTransaccion():
    pass

def consultaUnBloque(hash):
    myquery={"_id":hash}
    mydoc=col.find(myquery)
    for x in mydoc:
        print(x["transacciones"])

def eliminarDatos():
    x=col.delete_many({})
    print(x.deleted_count,"documents deleted")
