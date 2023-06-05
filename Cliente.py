# Elaborado por Trinidad González Alan Isaac
import socket

def recv_message(socket): # Aqui recibimos un mensaje del servidor a través del socket del cliente
    message_length = int.from_bytes(socket.recv(4), 'big')  # Aqui recibimos los primeros 4 bytes del socket que representan la longitud del mensaje
    return socket.recv(message_length)  # Aqui recibimos los bytes del mensaje según la longitud especificada

def send_message(socket, message): # Envía un mensaje al servidor a través del socket del cliente
    message_bytes = message.encode()  # Codifica el mensaje a una secuencia de bytes
    socket.sendall(len(message_bytes).to_bytes(4, 'big'))  # Envía los 4 bytes que representan la longitud del mensaje
    socket.sendall(message_bytes)  # Envía los bytes del mensaje

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = input("Ingresa el host para el servidor: ")
PORT = int(input("Ingresa el puerto para el servidor: "))

client_socket.connect((HOST, PORT))

while True:
    turn_info = recv_message(client_socket).decode()  # Recibimos el estado del turno del servidor
    print(turn_info)

    if "Tu turno" in turn_info:
        board_str = recv_message(client_socket).decode()  # Recibimos la representación del tablero del servidor
        print(board_str)

        card_1_pos = input("Ingresa la posición de la primera carta (fila y columna, ej. 00) o 'exit' para salir: ")
        if card_1_pos == "exit":
            send_message(client_socket, "exit")
            break
        send_message(client_socket, card_1_pos)  # Enviamos la posición de la primera carta al servidor

        board_str = recv_message(client_socket).decode()  # Recibimos la representación actualizada del tablero del servidor
        print(board_str)

        card_2_pos = input("Ingresa la posición de la segunda carta (fila y columna, ej. 00): ")
        try:
            send_message(client_socket, card_2_pos)  # Enviamos la posición de la segunda carta al servidor
        except BrokenPipeError: # Caso para evitar que salga error de BrokenPipeError
            print("El servidor ha cerrado la conexión inesperadamente.")
            break

        board_str = recv_message(client_socket).decode()  # Recibimos la representación actualizada del tablero después de las jugadas
        print(board_str)

        message = recv_message(client_socket).decode()  # Recibimos el mensaje del servidor
        print(message)

        if "Felicidades" in message:
            break
        else:
            print("Esperando su turno")
    elif "Esperando tu turno" in turn_info:
        board_str = recv_message(client_socket).decode()  # Recibimos la representación actualizada del tablero del servidor
        print(board_str)

        message = recv_message(client_socket).decode()  # Recibimos el mensaje del servidor
        print(message)
        continue

client_socket.close()
