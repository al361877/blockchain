import BlockchainController
from blockchain.red.servidorPrueba import ServidorPrueba

if __name__=="__main__":
    servidor=ServidorPrueba()
    print(servidor.clientes)
    servidor.start()
    BlockchainController.app.run(debug=True, port=8000)


