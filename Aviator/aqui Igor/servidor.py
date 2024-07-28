import socket
import threading
import time
import random

clients = {}
current_multiplier = 1.0
is_game_running = False

def handle_client(client_socket, addr):
    global is_game_running, current_multiplier
    clients[addr] = {"socket": client_socket, "balance": 1000.0}
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith("BET"):
                bet_amount = float(message.split()[1])
                if clients[addr]["balance"] >= bet_amount:
                    clients[addr]["balance"] -= bet_amount
                    client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}".encode())
                    if not is_game_running:
                        is_game_running = True
                        current_multiplier = 1.0
                        threading.Thread(target=game_loop).start()
                else:
                    client_socket.send("INSUFFICIENT_FUNDS".encode())
            elif message.startswith("CASHOUT"):
                multiplier = float(message.split()[1])
                bet_amount = float(message.split()[2])
                winnings = bet_amount * multiplier
                clients[addr]["balance"] += winnings
                client_socket.send(f"WINNINGS {winnings:.2f}".encode())
                client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}".encode())
            elif message == "BALANCE":
                client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}".encode())
        except (ConnectionResetError, BrokenPipeError):
            del clients[addr]
            break

def game_loop():
    global is_game_running, current_multiplier
    stop_multiplier = random.uniform(1.0, 20.0)
    while is_game_running:
        current_multiplier += 0.1
        for client in clients.values():
            try:
                client["socket"].send(f"MULTIPLIER {current_multiplier:.2f}".encode())
            except (ConnectionResetError, BrokenPipeError):
                pass
        time.sleep(0.2)
        if current_multiplier >= stop_multiplier:
            is_game_running = False
            for client in clients.values():
                try:
                    client["socket"].send("STOPPED".encode())
                except (ConnectionResetError, BrokenPipeError):
                    pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server started on port 9999.")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
