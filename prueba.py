from hashlib import sha256
from blockchain.Modelo.Block import Block
import time
if __name__=="__main__":
    print(sha256("HOLA".encode()).hexdigest())
    bloque=Block(0,"HOLA",time.time(),"0","token")

    print(bloque.compute_hash())

    print(bloque.compute_hash())
    print(bloque.compute_hash())
    print(bloque.compute_hash())

