from socket import socket
# Compatibilidad con Python 3
class Cliente():
    def __init__(self):
        self.ipServer="localhost"

    def enviar(self,output_data):
        s = socket()
        s.connect((self.ipServer, 6030))

        if output_data:
            # Enviar entrada. Comptabilidad con Python 3.
            try:
                s.send(output_data)
            except TypeError:
                s.send(bytes(output_data, "utf-8"))

            # Recibir respuesta.
            input_data = s.recv(1024)
            if input_data:
                # En Python 3 recv() retorna los datos leídos
                # como un vector de bytes. Convertir a una cadena
                # en caso de ser necesario.
                input_data=input_data.decode("utf-8")
                if input_data!="ok":
                    if input_data=="not ok":
                        print("algun nodo no me acepta")
                    print("La lista de IPs es:",end="")
                    lista=input_data.split("#")
                    print(lista)
                else:
                    print("Ha sido minado con exito")

if __name__ == "__main__":
    cliente=Cliente()
    while True:
        data=input("> ")
        cliente.enviar(data)
