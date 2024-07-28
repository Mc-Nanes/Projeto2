import socket
import threading
import time
import random

clients = {}
current_multiplier = 1.0
is_game_running = False
previous_multipliers = []
lock = threading.Lock()

def handle_client(client_socket, addr):
    global is_game_running, current_multiplier
    with lock:
        clients[addr] = {"socket": client_socket, "balance": 1000.0}
        send_message_to_all_clients(f"CLIENTS_CONNECTED {len(clients)}|")
        client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}|".encode())
        if previous_multipliers:
            for multiplier in previous_multipliers:
                client_socket.send(f"PREVIOUS_MULTIPLIER {multiplier:.2f}|".encode())
    while True:
        try:
            message = client_socket.recv(1024).decode().strip()
            if not message:
                continue

            if message.startswith("BET"):
                parts = message.split()
                if len(parts) >= 2:
                    bet_amount = float(parts[1].replace('|', ''))
                    if clients[addr]["balance"] >= bet_amount:
                        with lock:
                            if not is_game_running:
                                clients[addr]["balance"] -= bet_amount
                                client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}|".encode())
                                is_game_running = True
                                current_multiplier = 1.0
                                threading.Thread(target=game_loop).start()
                            else:
                                client_socket.send("GAME_RUNNING|".encode())
                    else:
                        client_socket.send("INSUFFICIENT_FUNDS|".encode())
            elif message.startswith("CASHOUT"):
                parts = message.split()
                if len(parts) >= 3:
                    multiplier = float(parts[1].replace('|', ''))
                    bet_amount = float(parts[2].replace('|', ''))
                    winnings = bet_amount * multiplier
                    with lock:
                        clients[addr]["balance"] += winnings
                    client_socket.send(f"WINNINGS {winnings:.2f}|".encode())
                    client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}|".encode())
            elif message == "BALANCE":
                client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}|".encode())
        except (ValueError, IndexError):
            client_socket.send("INVALID_MESSAGE|".encode())
        except (ConnectionResetError, BrokenPipeError):
            break

    with lock:
        del clients[addr]
        send_message_to_all_clients(f"CLIENTS_CONNECTED {len(clients)}|")
    client_socket.close()

def game_loop():
    global is_game_running, current_multiplier, previous_multipliers
    stop_multiplier = random.uniform(1.0, 20.0)
    while is_game_running:
        current_multiplier += 0.1
        for client in clients.values():
            try:
                client["socket"].send(f"MULTIPLIER {current_multiplier:.2f}|".encode())
            except (ConnectionResetError, BrokenPipeError):
                pass
        time.sleep(0.2)
        if current_multiplier >= stop_multiplier:
            is_game_running = False
            previous_multipliers.append(current_multiplier)
            if len(previous_multipliers) > 6:
                previous_multipliers.pop(0)
            for client in clients.values():
                try:
                    client["socket"].send("STOPPED|".encode())
                except (ConnectionResetError, BrokenPipeError):
                    pass
            time.sleep(3)  # Pausa de 3 segundos entre as rodadas

def send_message_to_all_clients(message):
    for client in clients.values():
        try:
            client["socket"].send(message.encode())
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
