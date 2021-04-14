from socket import socket, error
from threading import Thread

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
                    bloque=input_data.decode("utf-8")

                    if bloque!="hello":
                        bloque=BlockchainController.mi_consenso(bloque)
                        if bloque:
                            BlockchainController.add_block_db(bloque)
                            #le digo al cliente que esta ok
                            self.conn.send(bytes("ok", "utf-8"))
                        else:
                            #le hago saber que no esta bien
                            self.conn.send(bytes("not ok", "utf-8"))
                    else:
                        # si es un hello, envio mi lista de ips
                        self.conn.send(bytes(self.lista, "utf-8"))


class ServidorPrueba():

    def __init__(self):
        self.clientes=BaseDeDatos.cargarNodos()

    def add_cliente(self,ip):
        self.clientes.append(ip)
        BaseDeDatos.addNodo(ip)


    def main(self):
        s = socket()

        # Escuchar peticiones en el puerto 6030.
        s.bind(("localhost", 6030))
        s.listen(0)

        while True:
            conn, addr = s.accept()
            c = Client(conn, addr)
            direccionesIP=""
            for ip in self.clientes:
                if ip != self.clientes[-1]:
                    direccionesIP=direccionesIP+str(ip)+"#"
                else:
                    direccionesIP=direccionesIP+str(ip)
            c.lista=direccionesIP
            c.start()
            ip=addr[0]

            if ip not in self.clientes:
                self.add_cliente(addr[0])
                print("Se ha añadido un nuevo nodo")




if __name__ == "__main__":

    servidor=ServidorPrueba()
    print(servidor.clientes)
    servidor.main()
