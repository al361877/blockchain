import json
from pprint import pprint
import os
import pymongo

from pymongo import MongoClient



myclient = pymongo.MongoClient('mongodb://localhost:27017/')

db=myclient['blockchain']
bloquesdb=db['bloques']
transaccionesdb=db['transacciones']
nodosdb=db['nodos']

#############################################
#Estas tablas solo seran para el nodo padre.#
#############################################

#tabla de logs
logsdb=db['logsTable']


#tabla de hahses
hashesdb=db['hashesTable']



###########################################################
#############         BLOQUES         #####################
###########################################################

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


#devuelve un bloque pasandole un indice como argumento, sirve para enviar bloque a bloque
def bloqueIndice(indice):
    myquery = {"indice": int(indice)}
    mydoc = bloquesdb.find(myquery)
    for x in mydoc:
        return x


def consultaNombre():
    return db.list_collection_names()



###########################################################
#############      TRANSACCIONES      #####################
###########################################################


#se almacenara la transaccion direcctamente, sin haber minado el bloque
def almacenar_transaccion(transaccion):
    transaccionesdb.insert({"_id": transaccion.hash, "hashDato": transaccion.hashDato,
             "bloque":"bloque no minado"})


#se pone la direccion del bloque ya minado
def update_transaccion(hashT,hashB):
    myquery={"_id":hashT}
    update={"$set":{"bloque":hashB}}
    transaccionesdb.update_one(myquery,update)

def consultaTransacciones():
    myquery={"bloque":"bloque no minado"}
    for x in transaccionesdb.find(myquery):
        yield x

def verificaTransaccion(hash):
    myquery = {"_id": hash}
    transaccion=False
    for x in transaccionesdb.find(myquery):
        transaccion=x

    if transaccion:
        print(transaccion["bloque"])
        #si esta en el nodo, pero no esta minado, no sirve, ya que significa que solo estara localmente.
        if transaccion["bloque"]=="bloque no minado":
            return False
    print(transaccion)
    #si sigue siendo false, significa que no esta en este nodo
    return transaccion

def almacenar_transaccion_block_aceptado(hashB,hashD,hashBlock):
    transaccionesdb.insert({"_id": hashB, "hashDato": hashD,
                            "bloque": hashBlock})

###########################################################
#############           NODOS         #####################
###########################################################

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



###########################################################
#############           LOGS          #####################
###########################################################
def almacenar_log(log):
    logsdb.insert(log.toDict())

#consulta los logs mediante el hash del dato
def consultar_log_hashD(hashD):
    myquery = {"hashDato": hashD}
    logs=[]
    for x in logsdb.find(myquery):
        logs.append(x)
    return logs

def consulta_log_user(user):
    myquery = {"user": user}
    logs = []
    for x in logsdb.find(myquery):
        logs.append(x)
    return logs

def consulta_log_fecha(fecha):
    myquery = {"fecha": fecha}
    logs = []
    for x in logsdb.find(myquery):
        logs.append(x)
    return logs

def consulta_log_motivo(motivo):
    myquery = {"motivo": motivo}
    logs = []
    for x in logsdb.find(myquery):
        logs.append(x)
    return logs

def consultaUltimoLog():
    log=logsdb.find().sort("indice",-1).limit(1)
    for x in log:

        return x


def elimina_logs():
    logsdb.delete_many({})

###########################################################
#############           HASH          #####################
###########################################################
def almacenar_hashes(hashDato,hashBlockchain):
    hashesdb.insert({"_id": hashDato, "hashBlockchain": hashBlockchain})

def consulta_hahses_hashDato(hashDato):
    myquery = {"_id": hashDato}
    hashes = []
    for x in hashesdb.find(myquery):
        hashes.append(x)
    return hashes

def consulta_hahses_hashB(hahsB):
    myquery = {"hashBlockchain": hahsB}
    hashes = []
    for x in hashesdb.find(myquery):
        hashes.append(x)
    return hashes

def elimina_hashes():
    hashesdb.delete_many({})


if __name__ == "__main__":
    myIP=os.getenv('MYIP')
    print(myIP)
