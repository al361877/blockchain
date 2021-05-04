from socket import socket
# Compatibilidad con Python 3
from blockchain.datos import BaseDeDatos


class Cliente():
    def __init__(self,ip):
        self.ipServer=ip

    def enviar(self,output_data):
        s = socket()
        s.connect((self.ipServer, 6030))

        if output_data:
            # Enviar entrada. Comptabilidad con Python 3.
            try:
                s.send(output_data)
            except TypeError:
                s.send(bytes(output_data, "utf-8"))


            # Recibir respuesta. Puede ser una respuesta al bloque, la lista de nodos o la blockchain
            input_data = s.recv(1024)
            if input_data:
                input_data=input_data.decode("utf-8")

                if input_data!="ok":
                    if input_data=="not ok":
                        return "not ok"

                    #puede ser la lista de ips o la blockchain, pero no me tengo que preocupar
                    #ya que si se llama cuando toca, tendrá el dato que necesita
                    lista=input_data.split("#")

                    return lista

                elif input_data=="ok":
                    return "ok"
                else:
                    return input_data

if __name__ == "__main__":
    cliente=Cliente()
    while True:
        data=input("> ")
        cliente.enviar(data)
