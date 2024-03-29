from pprint import pprint

from flask import Flask, request, render_template
import time
from modelos.Blockchain import Blockchain

import json
from modelos.Block import Block
from modelos.Log import Log
from datos import BaseDeDatos
from red.Cliente import Cliente

soyPadre=False
app =  Flask(__name__)
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
padre="10.129.84.108"
# la dirección the otros miembros que participan en la red
peers = set()
blockchain=Blockchain()


@app.route('/')
def home():
    compruebaBlockchain()

    return render_template("home.html")



######################################################################
#############         CONTROLADOR VISTA          #####################
######################################################################

@app.route('/borrar',methods=['GET'])
def reset():
    resetearBlockchain()
    return render_template("home.html")


@app.route('/add', methods=['POST'])
def newTransactionController():

    #hash del dato de la transacción
    hashDato = request.form['transaccionDatos']

    usuario=request.form['user']

    hashB=None
    transaccion=blockchain.add_new_transaction(hashDato)
    if transaccion:
        hashB=transaccion.hash
        almacenarTransaccion(transaccion)
        guardar_log_registro(usuario,hashDato,hashB)


    return render_template("home.html",consultaT=True,token=hashB)

@app.route('/consulta', methods=['POST'])
def consulta():
    usuario = request.form['user']
    #es el hashDato
    hash=request.form['consulta']
    guardar_log_consulta(usuario,hash)

    nodos = BaseDeDatos.cargarNodos()

    #primero miro en el servidor
    consulta = BaseDeDatos.consulta_hahses_hashDato(hash)


    # guardo todas las respuestas
    respuestas = []

    # envio el bloque a todos los nodos de la blockchain
    for ipNodo in nodos:
        try:
            cliente = Cliente(ipNodo)
            respuesta = cliente.enviar(("hashB",hash))
            respuestas.append(respuesta)
        except:
            print("El nodo con ip {} no esta conectado")
    # cuento las respuestas ok, si estas son igual al numero de nodos
    contadorOk = 0
    for respuesta in respuestas:
        if respuesta == "ok":
            contadorOk += 1
    if contadorOk == len(nodos):
        return render_template("home.html", resultadoConsulta="la transaccion esta correctamente en la blockchain", respuestaConsulta=True)

    if consulta:
        #significa que en el servidor está mal
        pass

    return render_template("home.html",resultadoConsulta="la transacción no se encuentra en la blockchain",respuestaConsulta=True)

@app.route('/chain', methods=['POST'])
def get_chain():

    chain_data = consultaBlockchain()
    for block in chain_data:
        print(block["transacciones"])

    return render_template("home.html",consulta=True,chain_data=chain_data)



@app.route('/mine', methods=['GET'])
def mine_unconfirmed_block():
    bloque = blockchain.mine()
    if bloque==-1:
        return render_template("home.html",minado=-1,indice=False)
    nodos= BaseDeDatos.cargarNodos()
    #guardo todas las respuestas
    respuestas=[]
    #envio el bloque a todos los nodos de la blockchain
    for ipNodo in nodos:
        try:
            cliente=Cliente(ipNodo)
            respuesta=cliente.enviar(json.dumps(bloque.__dict__, sort_keys=False))
            respuestas.append(respuesta)
        except:
            print("El nodo con ip {} no esta conectado")
    #cuento las respuestas ok, si estas son igual al numero de nodos
    contadorOk=0
    for respuesta in respuestas:
        if respuesta=="ok":
            contadorOk+=1
    #lo guardo en mi blockchain y le digo al resto de nodos que lo guarden
    if contadorOk== len(respuestas):
        guardar_bloque(bloque)
        for ipNodo in nodos:
            try:
                cliente=Cliente(ipNodo)
                cliente.enviar("confirmado")
            except:
                print("El nodo con ip {} no esta conectado")



    result=bloque.get_indice()

    return render_template("home.html",minado=1,indice=result)


######################################################################
#############         CAPA SERVICIOS             #####################
######################################################################



#este metodo primero mira si hay una blockchain ya creada, si lo está "la carga", si no la crea
def compruebaBlockchain():

    #este metodo devuelve el primer bloque, es decir, el genesis
    bloqueGenesis= BaseDeDatos.encuentraUnBloque()
    blockchain.set_genesis(bloqueGenesis)

    if bloqueGenesis:
        #si existe la base de datos solo tengo que cargar el 'ultimo bloque
        bloque=consultaUltimoBloque()

        #creo el nuevo bloque, que será una copia del último añadido en la bbdd
        block=construirBloque(bloque)
        blockchain.cargarBlock(block)

        #miro las últimas transacciones no minadas y se las añado al bloque sin minar de mi blockchain
        transacciones=consultaTransacciones()

        #despues de haber cargado mi base de datos, actualizo
        actuaizar()

        for transaccion in transacciones:
            blockchain.add_transaccion_minada(transaccion)

    else:
        #el padre si es nuevo no se tiene que registrar
        #tiene que crear el bloque genesis
        if soyPadre:
            blockchain.crear_genesis_block()
        else:
            #si no existe un bloque genesis, es que soy nuevo y me registro
            register_me()




'''Construye un bloque objeto a partir de un boque diccionario, que es el que te da la base de datos'''
def construirBloque(bloque):
    block = Block()
    print("hash del bloque",bloque["_id"])
    block.set_hash(bloque["_id"])
    block.indice = int(bloque["indice"])
    block.transacciones = bloque["transacciones"]

    block.prev_hash = bloque["prev_hash"]
    block.Nonce = bloque["Nonce"]
    block.MAX_TRANS = bloque["MAX_TRANS"]
    block.trabajo = bloque["trabajo"]
    return block


#este metodo se usa cuando llega un nuevo nodo a la blockchain
def register_me():
    nodoPadre=padre
    #enviar un hello al nodo padre, esta ip luego será una variable de entorno
    cliente=Cliente(nodoPadre)
    listaIP=cliente.enviar("hello padre")

    addNodo(nodoPadre)
    myIP="10.129.84.107"
    if listaIP!="no hay nodos":
        for ip in listaIP:
            try:
                if ip != myIP and ip != nodoPadre:
                    print("envio hello a",ip)
                    #una vez tengo la lista de ips, voy a enviar un hello a todos los dem'as nodos para que me agreguen a su lista
                    nuevoCliente=Cliente(ip)
                    nuevoCliente.enviar("hello")

            except:
                print("El nodo con ip {} no esta conectado".format(ip))

    solicitar_blockchain()



def actuaizar():
    '''
    este metodo es similar al anterior de registrarme, pero con la diferencia de que se ejecuta cada vez que arranco el programa
    se diferencia sobretodo en que tiene que comparar lo que ya tiene con los nuevos datos para que no guarde cosas repetidas.
    '''
    cliente=Cliente(padre)
    listaIPNueva=cliente.enviar("hello padre")
    myIP="10.129.84.107"
    #cojo mi lista de ips para comparar si se ha unido alguien nuevo, y si lo ha hecho, agregarlo
    miListaIP=cargarNodos()

    for nuevaIp in listaIPNueva:
        if nuevaIp!=myIP:
            if nuevaIp not in miListaIP:
                print("la ip {} no estaba en mi lista".format(nuevaIp))
                addNodo(nuevaIp)
                #no hace falta enviar el hello al nodo, este ya tendrá mi ip, porque se la habrá dado el padre

    #solicito último bloque y lo comparto con el mio, si no es el mismo, solicito la blockchain desde el indice de mi bloque.
    miUltimoBloque=consultaUltimoBloque()
    print("mi ultimo bloque",miUltimoBloque)
    miUltimoBloque=construirBloque(miUltimoBloque)

    #le solicito el ultimo bloque al padre
    ultimoBloqueBlockchain=cliente.enviar("ultimoBloque")

    print("su bloque",ultimoBloqueBlockchain[0])
    ultimoBloqueBlockchain=construirBloque(json.loads(ultimoBloqueBlockchain[0]))
    #comparo el hash. Si no coinciden, solicito la blockchain desde el indice de mi último bloque
    if miUltimoBloque.get_hash()!=ultimoBloqueBlockchain.get_hash():
        indice=miUltimoBloque.indice
        for i in range(int(indice),int(ultimoBloqueBlockchain.indice)):
            string="Indice"+"#"+str(i+1)
            guardar_bloque(construirBloque(json.loads(cliente.enviar(string)[0])))




def solicitar_blockchain():
    cliente=Cliente(padre)
    lenBlockchain=cliente.enviar("solicitud")[0]

    for i in range(0,int(lenBlockchain)):
        string="Indice"+"#"+str(i)
        guardar_bloque(construirBloque(json.loads(cliente.enviar(string)[0])))






def mi_consenso(bloque):
    """"
    Mi consenso se realizará de la siguiente manera. Primero el bloque tienen que encontrar un hash adecuado con la prueba de trabajo
    cuando lo haya logrado, compartirá el bloque, para que el resto verifiquen que con ese nonce y esa fecha se cumple la prueba de trabajo
    entonces todos añadirán el bloque a su cadena de bloques.
    """
    return blockchain.prueba_de_minado(bloque)


def guardar_bloque(bloque):
    """
    Despues de que el bloque haya sido aceptado por el consenso, todos lo guardan en su blockchain
    Este metodo es llamado desde el servidor que ha confirmado el bloque
    """
    #lo agrego a la blockchain local y a la de la base de datos
    blockchain.add_definitivo(bloque)
    add_block_db(bloque)


def guardar_transacciones(bloque):
    print("guardo transacciones")
    transacciones=bloque.get_transacciones()
    print("las transacciones son: ",transacciones)
    for transaccion in transacciones:
        print("la tansaccion es : ",transaccion, "el value es:",transacciones[transaccion],"y el hash del bloque es",bloque.get_hash())
        BaseDeDatos.almacenar_transaccion_block_aceptado(transaccion, transacciones[transaccion], bloque.get_hash())

def confirmado():
    bloque=blockchain.bloque_consenso
    print(bloque)
    guardar_bloque(bloque)
    guardar_transacciones(bloque)


##############     A PARTIR DE AQUI, VOY A TRATAR CON LA BASE DE DATOS        ##############

def almacenar():
    '''
    Aqui almacenaré la blockchain, para poder disponer de ella una vez vuelva
    a ejecutar el programa o después de volver a arrancar la máquina
    '''

    #almaceno el 'ultimo bloque
    global blockchain
    BaseDeDatos.almacenarBlockchain(blockchain.get_cadena())

def consultaBloque(hash):
    bloque = []
    for dato in BaseDeDatos.consultaUnBloque(hash):
        bloque.append(dato)
    return bloque


def consultaTransaccion(hashT):
    transaccion = []
    for dato in BaseDeDatos.consultaUnaTransaccion(hashT):
        transaccion.append(dato)
    return transaccion


def consultaBlockchain():
    blockchain=[]
    for block in BaseDeDatos.consultaDatos():
        blockchain.append(block)
    return blockchain

def add_block_db(block):
    '''''
    En este caso, este metodo guardara el bloque en la base de datos, en vez de localmente en el programa.
    '''
    BaseDeDatos.almacenarBloque(block)

def add_genesis(genesis):
    BaseDeDatos.almacenar_genesis(genesis)

def resetearBlockchain():
    BaseDeDatos.eliminarDatos()
def consultaNombre():
    return BaseDeDatos.consultaNombre()

def consultaUltimoBloque()-> Block:
    return BaseDeDatos.consultaUltimoBloque()


def almacenarTransaccion(transaccion):
    BaseDeDatos.almacenar_transaccion(transaccion)

#mira las ultimas transacciones que no han sido minadas
def consultaTransacciones():
    transacciones=[]
    for transaccion in BaseDeDatos.consultaTransacciones():
        transacciones.append(transaccion)
    return transacciones
def cargarNodos():
    return BaseDeDatos.cargarNodos()

def addNodo(ip):
    BaseDeDatos.addNodo(ip)

########### LOGS ############

def guardar_log_registro(usuario,hashDato,hashBlockchain):

    #primero miro el indice del ultimo log
    ultimoLog= BaseDeDatos.consultaUltimoLog()
    #si no existe ningun log, significa que este es el primero y el indice sera 1
    if ultimoLog:
        indice=ultimoLog['indice']
        miIndice = int(indice) + 1
        log = Log(miIndice,usuario,time.ctime(time.time()),hashDato,hashBlockchain,"Registro")
    else:
        log = Log(0, usuario, time.ctime(time.time()), hashDato,hashBlockchain, "Registro")

    BaseDeDatos.almacenar_log(log)




def guardar_log_consulta(usuario,hashDato):
    # primero miro el indice del ultimo log
    ultimoLog = BaseDeDatos.consultaUltimoLog()
    # si no existe ningun log, significa que este es el primero y el indice sera 1
    if ultimoLog:
        indice = ultimoLog['indice']
        miIndice = int(indice) + 1
        log = Log(miIndice, usuario, time.ctime(time.time()), hashDato, "Consulta")

    else:
        log = Log(0, usuario, time.ctime(time.time()), hashDato, "Consulta")

    BaseDeDatos.almacenar_log(log)

######### HASHES #############
def guardar_hashes(hashDato,hashB):
    BaseDeDatos.almacenar_hashes(hashDato, hashB)


