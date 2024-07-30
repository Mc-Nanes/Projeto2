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
                    with lock:
                        if clients[addr]["balance"] >= bet_amount:
                            clients[addr]["balance"] -= bet_amount
                            client_socket.send(f"BALANCE {clients[addr]['balance']:.2f}|".encode())
                        else:
                            client_socket.send("INSUFFICIENT_FUNDS|".encode())

            elif message.startswith("CASHOUT"):
                with lock:
                    multiplier = current_multiplier
                    bet_amount = float(parts[1].replace('|', ''))
                    winnings = bet_amount * multiplier
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
    vertical_position = 0.0
    vertical_direction = random.choice([-1, 1])  # -1 para descida, 1 para subida

    while is_game_running:
        with lock:
            current_multiplier += 0.1
            position = current_multiplier * 50  # Cálculo da posição do avião

            # Atualizar a posição vertical
            vertical_position += vertical_direction * 5
            # Alterar direção aleatoriamente
            if random.random() < 0.1:
                vertical_direction *= -1

            send_message_to_all_clients(f"MULTIPLIER {current_multiplier:.2f}|POSITION {position:.2f},{vertical_position:.2f}|")
        
        time.sleep(0.2)
        if current_multiplier >= stop_multiplier:
            is_game_running = False
            previous_multipliers.append(current_multiplier)
            if len(previous_multipliers) > 6:
                previous_multipliers.pop(0)
            send_message_to_all_clients("STOPPED|")
            auto_start_game()

def send_message_to_all_clients(message):
    for client in clients.values():
        try:
            client["socket"].send(message.encode())
        except (ConnectionResetError, BrokenPipeError):
            pass

def auto_start_game():
    time.sleep(10)
    global is_game_running, current_multiplier
    with lock:
        if not is_game_running:
            is_game_running = True
            current_multiplier = 1.0
            threading.Thread(target=game_loop).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server started on port 9999.")

    threading.Thread(target=auto_start_game).start()

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
