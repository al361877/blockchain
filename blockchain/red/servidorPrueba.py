from socket import socket, error
from threading import Thread

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
                # Reenviar la información recibida.
                if input_data:
                    print("he recivido",input_data.decode("utf-8"))
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
