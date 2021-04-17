from hashlib import sha256
from blockchain.Modelo.Block import Block
import time
if __name__=="__main__":
    print("hash de HOLA",sha256("HOLA".encode()).hexdigest())


