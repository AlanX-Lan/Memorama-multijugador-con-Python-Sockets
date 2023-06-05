# Elaborado por Trinidad González Alan Isaac
import socket  
import random 
import time  
import threading  
from threading import Barrier, Lock 

def handle_client(connection, address, player_number, board, revealed, lock, barrier, turn, clients):
    # Aqui manejamos la comunicación con un cliente conectado
    print(f"Jugador {player_number} se ha unido desde {address}.")
    matches = 0
    waiting = False
    while matches < (len(board) * len(board[0])) // 2:
        barrier.wait()  # Esperamos a que todos los jugadores se unan
        while True:
            with lock:
                if turn[0] != player_number:
                    if not waiting:
                        send_message(connection, "Esperando tu turno")
                        waiting = True
                    continue
                else:
                    waiting = False

                send_message(connection, "Tu turno")
                board_string = ""
                # Aqui construimos una representación del tablero para enviar al cliente
                for i in range(len(board)):
                    row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                    board_string += row_str + "\n"
                send_message(connection, board_string)

                card_1_pos = recv_message(connection).decode()
                if card_1_pos == "exit":
                    send_message(connection, "¡Juego cancelado por el usuario!")
                    break
                card_1_row, card_1_col = int(card_1_pos[0]), int(card_1_pos[1])
                revealed[card_1_row][card_1_col] = True

                # Generamos el tablero después de revelar la primera carta
                board_string = ""
                for i in range(len(board)):
                    row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                    board_string += row_str + "\n"
                send_message(connection, board_string)

                card_2_pos = recv_message(connection).decode()
                card_2_row, card_2_col = int(card_2_pos[0]), int(card_2_pos[1])
                revealed[card_2_row][card_2_col] = True

                # Generamos el tablero después de revelar la segunda carta
                board_string = ""
                for i in range(len(board)):
                    row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                    board_string += row_str + "\n"

                if board[card_1_row][card_1_col] == board[card_2_row][card_2_col]:
                    matches += 1
                    message = "¡Cartas iguales! "
                    if matches == (len(board) * len(board[0])) // 2:
                        message += "¡Felicidades! Has completado el memorama."
                    else:
                        message += f"Llevas {matches} de {(len(board) * len(board[0])) // 2} parejas encontradas."
                else:
                    message = "¡Cartas diferentes! Sigue intentando."
                    time.sleep(2)
                    revealed[card_1_row][card_1_col] = False
                    revealed[card_2_row][card_2_col] = False

                # Enviamos la representación del tablero y el mensaje al jugador actual
                send_message(connection, board_string)
                send_message(connection, message)

                # Enviamos la representación del tablero y el mensaje a los demás jugadores
                for client in clients:
                    if client != connection:
                        send_message(client, board_string)
                        send_message(client, message)

                turn[0] = (turn[0] + 1) % num_players  # Actualizamos el turno
                break
    connection.close()


def send_message(connection, message): # Envía un mensaje al cliente a través del socket
    message_bytes = message.encode() # Codifica el mensaje en formato de bytes.
    connection.sendall(len(message_bytes).to_bytes(4, 'big')) # Convierte la longitud del mensaje en un entero de 4 bytes y lo envía al cliente
    connection.sendall(message_bytes) # Envía el mensaje en bytes al cliente


def recv_message(connection): # Aqui recibimos un mensaje del cliente a través del socket
    message_length = int.from_bytes(connection.recv(4), 'big')# Aqui recibimos los primeros 4 bytes del socket y los convierte a un entero que representa la longitud del mensaje
    return connection.recv(message_length) # Aqui recibimos el mensaje del cliente utilizando la longitud obtenida anteriormente


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.1.75"  # Dirección IP del servidor
PORT = 44000  # Puerto en el que el servidor escucha las conexiones

server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Servidor escuchando en {HOST}:{PORT}")

num_players = int(input("Ingrese el número de jugadores que se conectarán: "))

BOARD_SIZE = 4
values = list(range(1, (BOARD_SIZE * BOARD_SIZE) // 2 + 1)) * 2
random.shuffle(values)
board = [[0] * BOARD_SIZE for i in range(BOARD_SIZE)]
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        board[i][j] = values.pop()
revealed = [[False for _ in range(len(board))] for _ in range(len(board[0]))]

lock = Lock()  # Utilizamos Lock como un mecanismo de exclusión mutua para controlar el acceso al tablero compartido por los jugadores
barrier = Barrier(num_players)  # Se utiliza Barrier para sincronizar los hilos de los jugadores antes de iniciar el juego
turn = [0]  # Variable compartida para controlar el turno
clients = []  # Lista de sockets de los clientes conectados

for player_number in range(num_players):
    connection, address = server_socket.accept()  # Espera y acepta una conexión entrante del cliente
    clients.append(connection)  # Agrega el socket del cliente a la lista de clientes conectados
    client_thread = threading.Thread(target=handle_client, args=(connection, address, player_number, board, revealed, lock, barrier, turn, clients))  # Crea un nuevo hilo para manejar la comunicación con el cliente
    client_thread.start()  # Inicia el hilo para atender al cliente

turn[0] = 0  # Inicializa el turno en 0
