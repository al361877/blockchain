


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
        self.__transacciones_no_confirmadas = []
        self.__cadena = []
        self.crear_genesis_block()
        self.__bloque_sin_minar=Block()

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


        hash=self.prueba_de_trabajo(genesis_block)

        genesis_block.set_hash(hash)

        self.__cadena.append(genesis_block)

        self.controller.add_genesis(genesis_block)


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

        #lo meto en la base de datos
        self.controller.add_block_db(block)

        return True

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
            hashT=self.__bloque_sin_minar.add_transaccion(transaction,time.ctime(time.time()))
        else:
            self.mine()
            bloqueNuevo=self.__bloque_sin_minar=Block()
            hashT=bloqueNuevo.add_transaccion(transaction,time.ctime(time.time()))
        return hashT

    def mine(self):

        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """

        #cojo el último bloque de la cadena para enlazarlo con el nuevo
        last_block = self.__cadena[-1]

        #cojo el bloque sin minar y lo mino
        bloque=self.__bloque_sin_minar
        bloque.indice=last_block.get_indice()+1
        bloque.fecha=time.ctime(time.time())
        bloque.prev_hash=last_block.get_hash()

        #hago la prueba de trabajo para crear un hash bueno y se lo añado
        proof = self.prueba_de_trabajo(bloque)
        self.add_block(bloque, proof)
        self.__bloque_sin_minar=Block()
        return bloque.get_indice()



    def get_cadena(self):
        return self.__cadena

    def get_transacciones(self):
        return self.__bloque_sin_minar.get_transacciones()





if __name__=="__main__":
    blockchain=Blockchain()
    for i in range(3):
        cadena="{}".format(i)
        hash=blockchain.add_new_transaction(cadena)


    blockchain.mine()
    bloque=blockchain.last_block()


    controller=BlockchainController
    print("hash ultima transaccion:" ,hash)

    print(controller.consultaBlockchain())
    print(controller.consultaTransaccion(hash))
    print(controller.consultaBloque(bloque.get_hash()))
    controller.eliminarDatos()








