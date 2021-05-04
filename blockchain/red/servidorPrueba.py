from socket import socket, error
from threading import Thread
import json
import BlockchainController
from blockchain.datos import BaseDeDatos


class Client(Thread):
    """
    Servidor eco - reenvía todo lo recibido.
    """
    lista=""
    def __init__(self, conn, addr):
        # Inicializar clase padre.
        Thread.__init__(self)

        self.conn = conn
        self.addr = addr
        ip=addr[0]
        puerto=addr[1]
        print("{}:{} se ha conectado.".format(ip,puerto))

    def run(self):
        while True:
            try:
                # Recibir datos del cliente.
                input_data = self.conn.recv(1024)

            except error:
                print("[%s] Error de lectura." % self.name)
                break
            else:

                if input_data:
                    msg=input_data.decode("utf-8")
                    #lista es una tuppla de 2 elementos, el primero es un string (blockchainID) para indicar que el segundo elemento de la lista es el id del ultimo bloque
                    lista = msg.split("#")

                    if lista[0] == "BlockchainIndice":
                        indice=lista[1]
                        #cojo la blockchain desde ese indice
                        nuevaBlockchain=BaseDeDatos.blockchainIndice(indice)
                        blockchainString=""
                        for bloque in nuevaBlockchain:
                            if bloque != nuevaBlockchain[-1]:
                                bloqueString = json.dumps(bloque)
                                blockchainString = blockchainString + str(bloqueString) + "#"
                            else:
                                bloqueString = json.dumps(bloque)
                                blockchainString = blockchainString + str(bloqueString)
                        self.conn.send(bytes(blockchainString, "utf-8"))

                    elif msg=="hello padre":
                        # si es un hello, envio mi lista de ips (solo si es el nodo padre, si no lo es, no hace nada)
                        direccionesIP = ""

                        nodos=BaseDeDatos.cargarNodos()
                        # construyo una cadena que tendra todas las ips de mis nodos, para poderselo enviar al nuevo
                        for ip in nodos:
                            if ip != nodos[-1]:
                                direccionesIP = direccionesIP + str(ip) + "#"
                            else:
                                direccionesIP = direccionesIP + str(ip)

                        self.conn.send(bytes(direccionesIP, "utf-8"))

                    elif msg=="solicitud":
                        bloques=""
                        bloquesBD=BaseDeDatos.consultaDatos()

                        for bloque in bloquesBD:
                            if bloque!=bloquesBD[-1]:
                                bloqueString=json.dumps(bloque)
                                bloques=bloques+str(bloqueString)+"#"

                            else:
                                bloqueString=json.dumps(bloque)
                                bloques = bloques + str(bloqueString)

                        #le envio los bloques en formato de cadena
                        self.conn.send(bytes(bloques, "utf-8"))
                    elif msg=="hello":

                        self.conn.send(bytes("ok", "utf-8"))

                    elif msg=="ultimoBloque":
                        bloque=BlockchainController.consultaUltimoBloque()
                        bloqueString=json.dumps(bloque.__dict__, sort_keys=False)
                        self.conn.send(bytes(bloqueString, "utf-8"))


                    else:

                        #envio el bloque al consenso, si se confirma, le doy el ok y lo guardo en mi blockchain, sino, le digo que es erroneo
                        bloque = BlockchainController.mi_consenso(msg)
                        if bloque:
                            BlockchainController.guardar_bloque(bloque)
                            # le digo al cliente que esta ok
                            self.conn.send(bytes("ok", "utf-8"))
                        else:
                            # le hago saber que no esta bien
                            self.conn.send(bytes("not ok", "utf-8"))



class ServidorPrueba(Thread):

    def __init__(self):
        Thread.__init__(self)
        try:
            self.clientes=BaseDeDatos.cargarNodos()
        except:
            self.clientes = []

    #añado el nodo a mi lista de nodos
    def add_cliente(self,ip):
        self.clientes.append(ip)
        BaseDeDatos.addNodo(ip)


    def run(self):
        s = socket()

        # Esta ip luego será una variable de entorno
        myIP="10.129.84.116"
        s.bind((myIP, 6030))
        s.listen(0)

        while True:
            conn, addr = s.accept()
            c = Client(conn, addr)
            ip=addr[0]

            if ip!=myIP:
                c.start()

                #si la ip del cliente no lo tenia en mi lista de nodos, lo agrego
                if ip not in self.clientes:
                    self.add_cliente(addr[0])
                    print("Se ha añadido un nuevo nodo")




if __name__ == "__main__":

    servidor=ServidorPrueba()
    print(servidor.clientes)
    servidor.main()
