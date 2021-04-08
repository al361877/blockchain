from pprint import pprint

from flask import Flask, request, render_template

import requests
from blockchain.Modelo.Bolckchain import Blockchain

import json
from blockchain.Modelo.Block import Block
from blockchain.datos import BaseDeDatos

app =  Flask(__name__)
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

# la dirección the otros miembros que participan en la red
peers = set()
blockchain=Blockchain()


@app.route('/')
def home():
    compruebaBlockchain()

    return render_template("home.html")

#este metodo primero mira si hay una blockchain ya creada, si lo está "la carga", si no la crea
def compruebaBlockchain():


    bloqueGenesis=BaseDeDatos.col.find_one()
    blockchain.set_genesis(bloqueGenesis)
    if bloqueGenesis:
        #si existe la base de datos solo tengo que cargar el 'ultimo bloque
        #bloque=consultaUltimoBloque()
        bloque=consultaUltimoBloque()

        block = Block()
        block.set_hash(bloque["_id"])
        block.indice = bloque["indice"]
        block.transacciones = bloque["transacciones"]
        block.fecha = bloque["fecha"]
        block.prev_hash = bloque["prev_hash"]
        block.Nonce = bloque["Nonce"]
        block.MAX_TRANS = bloque["MAX_TRANS"]
        block.trabajo = bloque["trabajo"]
        blockchain.cargarBlock(block)

    else:
        blockchain.crear_genesis_block()

@app.route('/borrar',methods=['GET'])
def reset():
    resetearBlockchain()

    return render_template("home.html")




@app.route('/add', methods=['POST'])
def new_transaction():

    #dato de la transacción
    tx_data = request.form['transaccionDatos']


    hashT=None
    transaccion=blockchain.add_new_transaction(tx_data)
    if transaccion:
        hashT=transaccion[0]

    return render_template("home.html",consultaT=True,token=hashT)

@app.route('/consulta', methods=['POST'])
def consulta():

    hash=request.form['consulta']
    resultadoConsulta= consultaTransaccion(hash)
    return render_template("home.html",resultadoConsulta=resultadoConsulta,respuestaConsulta=True)

@app.route('/chain', methods=['POST'])
def get_chain():

    chain_data = consultaBlockchain()
    for block in chain_data:
        print(block["transacciones"])

    return render_template("home.html",consulta=True,chain_data=chain_data)



@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    compruebaBlockchain()
    bloque = blockchain.mine()
    if bloque==-1:
        return render_template("home.html",minado=-1,indice=False)

    result=bloque.get_indice()
    add_block_db(bloque)
    return render_template("home.html",minado=1,indice=result)


# punto de acceso para añadir nuevos compañeros a la red.
@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    #nodes = request.get_json()
    nodes=request.form["direccion"]
    print(nodes)
    if not nodes:
        return "Invalid data", 400
    for node in nodes:
        print(node)
        peers.add(node)

    return "Success", 201

@app.route('/add_me',methods=['POST'])
def register_me():
    direccion=request.form["direccion"]
    #broadcast a toda la red con mi dirección ip, para que me añadan y que me devuelvan la lista de peers


# punto de acceso para obtener los bloques
# no confirmados
# @app.route('/pending_tx')
# def get_pending_tx():
#     blockchain=blockchain1[-1]
#     return json.dumps(blockchain.get_transacciones())

def mi_consenso():
    """"
    Mi consenso se realizará de la siguiente manera. Primero el bloque tienen que encontrar un hash adecuado con la prueba de trabajo
    cuando lo haya logrado, compartirá el bloque, para que el resto verifiquen que con ese nonce y esa fecha se cumple la prueba de trabajo
    entonces todos añadirán el bloque a su cadena de bloques.
    """


def guardar_bloque(bloque):
    """
    Despues de que el bloque haya sido aceptado por el consenso, todos lo guardan en su blockchain
    """


def consensus():
    """
    Nuestro simple algoritmo de consenso. Si una cadena válida más larga es
    encontrada, la nuestra es reemplazada por ella.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain)

    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False



# punto de acceso para añadir un bloque minado por alguien más a la cadena del nodo.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():

    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"],
                  block_data["timestamp", block_data["previous_hash"]])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))

def fetch_posts():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],reverse=True)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Punto de acceso para crear una nueva transacción vía nuestra
    aplicación.
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return render_template('/')


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

def consultaUltimoBloque():
    return BaseDeDatos.consultaUltimoBloque()