import json
import time

import BlockchainController
from blockchain.Modelo.Block import Block

from blockchain.datos import BaseDeDatos


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2
    trabajo='abc'

    controller = BlockchainController
    def __init__(self):

        self.__cadena = []
        self.__bloque_sin_minar=Block()
        self.genesis=0

    def crear_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block()
        genesis_block.indice=0
        genesis_block.transacciones="genesis"
        genesis_block.fecha=time.ctime(time.time())

        print("Creo el genesis")
        hash=self.prueba_de_trabajo(genesis_block)

        genesis_block.set_hash(hash)

        self.__cadena.append(genesis_block)

        self.controller.add_genesis(genesis_block)

        self.genesis=genesis_block

    def set_genesis(self,genesis):
        self.genesis=genesis
    def last_block(self):
        return self.__cadena[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """

        previous_hash = self.__cadena[-1].get_hash()

        #comprueba si el último bloque que hay en la lista de bloques, es el mismo al que apunta mi bloque, si no es el correcto, de
        #devuelvo falso y termino
        if previous_hash != block.get_prev_hash():

            return False

        #comprueba que el bloque sea valido, si no lo es, devuelvo falso
        if not self.is_valid_proof(block, proof):

            return False

        #le asigno el hash al bloque
        block.set_hash(proof)


        #lo añado en la cadena
        self.__cadena.append(block)



        return True

    def cargarBlock(self,block):

        self.__cadena.append(block)
        print("cargo el ultimo bloque",block)

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """

        return (block_hash.startswith(self.trabajo) and block_hash == block.compute_hash())

    def prueba_de_trabajo(self, block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """


        computed_hash = block.compute_hash()

        while not computed_hash.startswith(self.trabajo):

            block.Nonce+=1
            computed_hash = block.compute_hash()

        return computed_hash


    def add_new_transaction(self, transaction):
        if transaction == " "*len(transaction):
            return False

        #si el bloque que tengo que minar aun no esta lleno, le meto la transacción, si ya lo está, lo mino y añado uno nuevo
        if(not self.__bloque_sin_minar.completo()):
            trans=self.__bloque_sin_minar.add_transaccion(transaction,time.ctime(time.time()))
        else:
            self.mine()
            bloqueNuevo=self.__bloque_sin_minar=Block()
            trans=bloqueNuevo.add_transaccion(transaction,time.ctime(time.time()))

        return trans
    def add_transaccion_minada(self,transaccion):
        if(not self.__bloque_sin_minar.completo()):
           self.__bloque_sin_minar.add_transaccion_minada(transaccion)
        else:
            self.mine()
            bloqueNuevo=self.__bloque_sin_minar=Block()
            bloqueNuevo.add_transaccion_minada(transaccion)

    def mine(self):

        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.genesis:
            self.crear_genesis_block()
        #cojo el último bloque de la cadena para enlazarlo con el nuevo
        last_block = self.__cadena[-1]

        #cojo el bloque sin minar y lo mino
        bloque=self.__bloque_sin_minar
        if not bloque.transacciones :
            return -1


        bloque.indice=last_block.get_indice()+1
        bloque.fecha=time.ctime(time.time())
        bloque.prev_hash=last_block.get_hash()

        #hago la prueba de trabajo para crear un hash bueno y se lo añado
        proof = self.prueba_de_trabajo(bloque)
        self.add_block(bloque, proof)
        self.__bloque_sin_minar=Block()

        return bloque


    def get_cadena(self):
        return self.__cadena


    def get_transacciones(self):
        return self.__bloque_sin_minar.get_transacciones()


    def prueba_de_minado(self,bloque):
    #el bloque me llega en formato json, por lo que para hacer la prueba de minado, primero creare el bloque con los datos del mismo y a ver si
    #cumple la prueba de trabajo

        block=Block()
        bloque=json.loads(bloque)



        block.indice=int(bloque["indice"])
        block.fecha=bloque["fecha"]
        block.Nonce=int(bloque["Nonce"])
        block.prev_hash=bloque["prev_hash"]
        block.transacciones=bloque["transacciones"]
        #una vez tengo el bloque hago la prueba de trabajo
        nuevoHash=block.compute_hash()
        block.set_hash(nuevoHash)
        # print("el hash del bloque es:",bloque["_id"],"mientras que el nuevo hash es:",nuevoHash)

        #para que sea valido, el nonce no se tiene que haber modificado y el hash tampoco
        if block.Nonce==int(bloque["Nonce"]) and bloque["_id"]==nuevoHash:
            return block
        else:
            print("ha habido un fallo")
            return False








