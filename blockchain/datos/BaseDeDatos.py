import json
from pprint import pprint

import pymongo

from pymongo import MongoClient


myclient = pymongo.MongoClient('mongodb://localhost:27017/')

db=myclient['blockchain']
bloquesdb=db['bloques']
transaccionesdb=db['transacciones']
nodosdb=db['nodos']

def almacenar_genesis(genesis):
    dato = genesis.__dict__
    bloquesdb.insert(dato)

def almacenarBloque(bloque):
    dato=bloque.__dict__
    bloquesdb.insert(dato)
    transacciones = bloque.get_transacciones()
    for transaccion in transacciones:
        update_transaccion(transaccion,bloque.get_hash())

def almacenarBlockchain(lista):
    for elemento in lista:
        almacenarBloque(elemento)


def consultaDatos():
    bloques=[]
    for x in bloquesdb.find():
        bloques.append(x)
    return bloques


def consultaUnaTransaccion(hash):
    myquery = {"_id": hash}
    mydoc = transaccionesdb.find(myquery)
    for x in mydoc:
        yield x

def consultaUnBloque(hash):
    myquery={"_id":hash}
    mydoc=bloquesdb.find(myquery)
    for x in mydoc:
        yield x

def eliminarDatos():
    x=bloquesdb.delete_many({})
    print(x.deleted_count,"documents deleted")
    y=transaccionesdb.delete_many({})
    print(y.deleted_count,"documents deleted")

#devuelve el primer bloque que encuentra, sirve para saber si tengo datos en la bbdd y asi cargar el ultimo bloque o no
def encuentraUnBloque():
    return bloquesdb.find_one()

def consultaUltimoBloque():
    bloque=bloquesdb.find().sort("indice",-1).limit(1)
    for x in bloque:

        return x

#devuelve la blockchain desde ese indice
def blockchainIndice(indice):
    nuevaBlockchain=[]
    ultimoBloque = consultaUltimoBloque()
    for i in range(indice,int(ultimoBloque["indice"])):
        myquery={"indice":i}
        for x in myquery:
            print(x)
            nuevaBlockchain.append(x)

    return nuevaBlockchain


def consultaNombre():
    return db.list_collection_names()

#se almacenara la transaccion direcctamente, sin haber minado el bloque
def almacenar_transaccion(transaccion):
    transaccionesdb.insert({"_id": transaccion.hash, "fecha": transaccion.fecha, "dato": transaccion.dato,
             "Nonce": transaccion.Nonce,"bloque":"bloque no minado"})


#se pone la direccion del bloque ya minado
def update_transaccion(hashT,hashB):
    myquery={"_id":hashT}
    update={"$set":{"bloque":hashB}}
    transaccionesdb.update_one(myquery,update)

def consultaTransacciones():
    myquery={"bloque":"bloque no minado"}
    for x in transaccionesdb.find(myquery):
        yield x

def addNodo(ip):

    nodosdb.insert({"ip":ip})

def consultaNodo(ip):
    myquery={"ip":ip}
    for x in nodosdb.find(myquery):
        return x
def cargarNodos():
    nodos=[]
    for nodo in nodosdb.find({}):
        nodos.append(nodo["ip"])
    return nodos
def eliminarNodos():
    nodosdb.delete_many({})

if __name__ == "__main__":
    eliminarNodos()
    eliminarDatos()
