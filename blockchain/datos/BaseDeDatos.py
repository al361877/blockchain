import json
from pprint import pprint

import pymongo

from pymongo import MongoClient


myclient = pymongo.MongoClient('mongodb://localhost:27017/')

db=myclient['blockchain']
col=db['bloques']
col2=db['transacciones']

def almacenar_genesis(genesis):
    dato = genesis.__dict__
    col.insert(dato)

def almacenarBloque(bloque):
    dato=bloque.__dict__
    col.insert(dato)
    transacciones = bloque.get_transacciones()
    for transaccion in transacciones:
        col2.insert(
            {"_id": transaccion, "fecha": transacciones[transaccion][0], "dato": transacciones[transaccion][1],
             "nonce": transacciones[transaccion][2]})

def almacenarBlockchain(lista):
    for elemento in lista:
        almacenarBloque(elemento)


def consultaDatos():
    for x in col.find():
        yield x


def consultaUnaTransaccion(hash):
    myquery = {"_id": hash}
    mydoc = col2.find(myquery)
    for x in mydoc:
        yield x

def consultaUnBloque(hash):
    myquery={"_id":hash}
    mydoc=col.find(myquery)
    for x in mydoc:
        yield x

def eliminarDatos():
    x=col.delete_many({})
    print(x.deleted_count,"documents deleted")
    y=col2.delete_many({})
    print(y.deleted_count,"documents deleted")


def consultaUltimoBloque():
    bloque=col.find().sort("indice",-1).limit(1)

    for x in bloque:

        return x

def consultaNombre():
    return db.list_collection_names()