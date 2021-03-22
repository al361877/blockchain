import time

from blockchain.Modelo.Block import Block
from hashlib import sha256
import random

from django.utils.crypto import get_random_string

class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.__transacciones_no_confirmadas = []
        self.__cadena = []
        self.crear_genesis_block()

    def crear_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, "genesis", time.time(), "0",0)

        genesis_block.hash = self.prueba_de_trabajo(genesis_block)

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
            return False

        #comprueba que el bloque sea valido, si no lo es, devuelvo falso
        if not self.is_valid_proof(block, proof):
            return False

        #le asigno el hash al bloque
        block.set_hash(proof)

        #lo añado en la cadena
        self.__cadena.append(block)


        return True

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """

        return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())

    def prueba_de_trabajo(self, block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """

        block.aleatorio=0
        computed_hash = block.compute_hash()

        while not computed_hash.startswith("0"*Blockchain.difficulty):
            block.aleatorio+=1
            computed_hash = block.compute_hash()

        print("Hash de",block.get_datos() ,"=",computed_hash)

        return computed_hash

    def add_new_transaction(self, transaction):
        # numeroRandom=str(random.randint(0,50))

        # #el token va a ser un identificativo de la transacción
        # token= sha256(numeroRandom.encode()).hexdigest()[:6]

        token = get_random_string(length=6)
        self.__transacciones_no_confirmadas.append((transaction,token))
        return token

    def mine(self):

        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.__transacciones_no_confirmadas:
            return False



        #cojo el último bloque de la cadena y lo minamos.
        last_block = self.__cadena[-1]

        ultima_transaccion=self.__transacciones_no_confirmadas.pop()

        #creo el bloque con los datos de la última transacción
        new_block = Block(last_block.get_indice() + 1,ultima_transaccion[0],time.time(),last_block.get_hash(),ultima_transaccion[1])

        #haga la prueba de trabajo para crear un hash bueno y se lo añado
        proof = self.prueba_de_trabajo(new_block)

        self.add_block(new_block, proof)


        return new_block.get_indice()

    #si está el token en la cadena de bloques, es que el bloque está y devuelvo True.
    #Si aun no se ha confirmado la transacción devolverá false y si no está en ningun lado es que el token no pertenece a ninguna transacción
    def consulta_transaccion(self,token):
        #aun no se ha confirmado la transacción
        for transaccion in self.__transacciones_no_confirmadas:
            if transaccion[1]==token:
                return False
        #la transacción ha sido confirmada y está el bloque creado
        for block in self.__cadena:
            if block.get_token() == token:
                return True

        #no existe esa transacción
        return -1

if __name__ == '__main__':
        arranque=Blockchain()
        token1=arranque.add_new_transaction("Hola pepe")
        token2=arranque.add_new_transaction("Adios pepe")
        arranque.mine()
        print(token1)
        print(token2)
        consulta=arranque.consulta_transaccion(token2)

        if(consulta==-1):
            print("No existe esa transacción")
        elif(consulta):
            print("Consulta confirmada")
        else:
            print("Aun no se ha confirmado la transacción")
