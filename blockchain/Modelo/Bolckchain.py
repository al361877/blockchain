from pprint import pprint

from django.utils.crypto import get_random_string
import time
from blockchain.Modelo.Block import Block

class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2
    trabajo='abc'

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
        genesis_block.datos="genesis"
        genesis_block.fecha=time.time()


        self.prueba_de_trabajo(genesis_block)



        self.__cadena.append(genesis_block)

    @property
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
            print("no coincide el hash")
            return False

        #comprueba que el bloque sea valido, si no lo es, devuelvo falso
        if not self.is_valid_proof(block, proof):
            print("no es valido")
            return False

        #le asigno el hash al bloque
        block.set_hash(proof)

        print("añado bloque")
        #lo añado en la cadena
        self.__cadena.append(block)


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

        print("Hash de",block.get_transacciones() ,"=",computed_hash)

        return computed_hash

    def add_new_transaction(self, transaction):
        if transaction is "":
            return False


        #si el bloque que tengo que minar aun no esta lleno, le meto la transacción, si ya lo está, lo mino y añado uno nuevo
        if(not self.__bloque_sin_minar.completo()):
            hashT=self.__bloque_sin_minar.add_transaccion(transaction,time.time())
        else:
            self.mine()
            bloqueNuevo=self.__bloque_sin_minar=Block()
            hashT=bloqueNuevo.add_transaccion(transaction,time.time())
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
        bloque.fecha=time.time()
        bloque.prev_hash=last_block.get_hash()

        #hago la prueba de trabajo para crear un hash bueno y se lo añado
        proof = self.prueba_de_trabajo(bloque)
        self.add_block(bloque, proof)

        return bloque.get_indice()

    # #si está el token en la cadena de bloques, es que el bloque está y devuelvo 1.
    # #Si aun no se ha confirmado la transacción devolverá -2 y si no está en ningun lado es que el token no pertenece a ninguna transacción y devolverá -1
    # def consulta_transaccion(self,token):
    #     #aun no se ha confirmado la transacción
    #     cadena=""
    #     for transaccion in self.__transacciones_no_confirmadas:
    #         if transaccion[1]==token:
    #
    #             return "La transacción con el token "+token+" aun no ha sido confirmada"
    #
    #     #la transacción ha sido confirmada y está el bloque creado
    #     for block in self.__cadena:
    #         if block.get_token() == token:
    #             return "La transacción con el token "+token+" ya ha sido confirmada"
    #
    #     #no existe esa transacción
    #     return "La transacción con el token "+token+" comprueba que hayas escrito correctamente el token."

    def get_cadena(self):
        return self.__cadena

    def get_transacciones(self):
        return self.__bloque_sin_minar.get_transacciones()

if __name__=="__main__":
    blockchain=Blockchain()
    for i in range(3):
        blockchain.add_new_transaction(i)
    pprint(blockchain.get_transacciones())
    blockchain.mine()
