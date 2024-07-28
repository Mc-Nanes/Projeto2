import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class BettingClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Betting Game Client")
        self.root.configure(bg='black')

        self.balance_var = tk.StringVar(value="0.00")
        self.multiplier_var = tk.StringVar(value="1.00x")
        self.bet_amount_var = tk.StringVar(value="")
        self.previous_multipliers = []

        self.setup_ui()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 9999))

        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.receiver_thread.start()
        self.client.send("BALANCE|".encode())  # Solicitar o saldo inicial do servidor

    def setup_ui(self):
        style = ttk.Style()
        style.configure('TLabel', foreground='white', background='black', font=('Exo 2', 14))
        style.configure('TButton', foreground='black', background='red', font=('Exo 2', 14, 'bold'))
        style.configure('TEntry', font=('Exo 2', 14))

        frame = ttk.Frame(self.root, padding="10 10 10 10", style="TFrame")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        header = ttk.Frame(frame, style="TFrame")
        header.grid(row=0, column=0, columnspan=2, pady=10)

        self.last_counters = ttk.Frame(header, style="TFrame")
        self.last_counters.grid(row=0, column=0, columnspan=2, pady=10)

        balance_label = ttk.Label(header, text="BALANCE:", style="TLabel", font=('Exo 2', 16, 'bold'), foreground='green')
        balance_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        balance_amount = ttk.Label(header, textvariable=self.balance_var, style="TLabel", font=('Exo 2', 16, 'bold'), foreground='white')
        balance_amount.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        mid_wrapper = ttk.Frame(frame, style="TFrame")
        mid_wrapper.grid(row=1, column=0, columnspan=2, pady=20)

        self.canvas = tk.Canvas(mid_wrapper, width=500, height=250, bg='black', highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=2)
        self.plane_image = Image.open("aqui_Igor/plane.png")
        self.plane_image = self.plane_image.resize((50, 50), Image.LANCZOS)
        self.plane_photo = ImageTk.PhotoImage(self.plane_image)
        self.plane_id = self.canvas.create_image(50, 125, image=self.plane_photo)

        counter_label = ttk.Label(mid_wrapper, textvariable=self.multiplier_var, style="TLabel", font=('Exo 2', 42, 'bold'), foreground='white')
        counter_label.grid(row=1, column=0, columnspan=2, pady=20)

        bottom_wrapper = ttk.Frame(frame, style="TFrame")
        bottom_wrapper.grid(row=2, column=0, columnspan=2, pady=20)

        bet_input = ttk.Entry(bottom_wrapper, textvariable=self.bet_amount_var, style="TEntry")
        bet_input.grid(row=0, column=0, padx=10, pady=10)

        self.bet_button = ttk.Button(bottom_wrapper, text="BET", command=self.place_bet, style="TButton")
        self.bet_button.grid(row=0, column=1, padx=10, pady=10)

        self.cashout_button = ttk.Button(bottom_wrapper, text="CASH OUT", command=self.cash_out, state=tk.DISABLED, style="TButton")
        self.cashout_button.grid(row=1, column=0, columnspan=2, pady=10)

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                buffer += self.client.recv(1024).decode()
                while "|" in buffer:
                    message, buffer = buffer.split("|", 1)
                    self.process_message(message)
            except (ConnectionResetError, BrokenPipeError):
                break

    def process_message(self, message):
        print(f"Received message: {message}")
        if message.startswith("MULTIPLIER"):
            multiplier = message.split()[1]
            self.multiplier_var.set(f"{multiplier}x")
            self.canvas.coords(self.plane_id, float(multiplier) * 50, 125)
        elif message == "STOPPED":
            self.canvas.coords(self.plane_id, 50, 125)
            multiplier = float(self.multiplier_var.get().replace('x', ''))
            self.previous_multipliers.append(multiplier)
            self.update_previous_multipliers()
            self.bet_button.config(state=tk.NORMAL)
            self.cashout_button.config(state=tk.DISABLED)
        elif message.startswith("WINNINGS"):
            winnings = float(message.split()[1])
            messagebox.showinfo("Betting Game", f"You won {winnings:.2f}!")
        elif message.startswith("BALANCE"):
            balance = float(message.split()[1])
            self.balance_var.set(f"{balance:.2f}")
        elif message == "GAME_RUNNING":
            messagebox.showinfo("Betting Game", "A game is already running. Please wait for the next round.")
        elif message == "INSUFFICIENT_FUNDS":
            messagebox.showerror("Betting Game", "You do not have enough funds to place this bet.")
        elif message.startswith("PREVIOUS_MULTIPLIER"):
            multiplier = float(message.split()[1])
            self.previous_multipliers.append(multiplier)
            self.update_previous_multipliers()
        elif message.startswith("CLIENTS_CONNECTED"):
            clients_connected = int(message.split()[1])
            print(f"Clients connected: {clients_connected}")

    def place_bet(self):
        bet_amount = self.bet_amount_var.get()
        if bet_amount:
            self.client.send(f"BET {bet_amount}|".encode())
            self.bet_button.config(state=tk.DISABLED)
            self.cashout_button.config(state=tk.NORMAL)

    def cash_out(self):
        current_multiplier = float(self.multiplier_var.get().replace('x', ''))
        bet_amount = self.bet_amount_var.get()
        if bet_amount:
            self.client.send(f"CASHOUT {current_multiplier} {bet_amount}|".encode())
            self.cashout_button.config(state=tk.DISABLED)

    def update_previous_multipliers(self):
        for widget in self.last_counters.winfo_children():
            widget.destroy()
        for multiplier in self.previous_multipliers:
            multiplier_label = ttk.Label(self.last_counters, text=f"{multiplier:.2f}x", style="TLabel", font=('Exo 2', 16, 'bold'), foreground='yellow')
            multiplier_label.pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    client = BettingClient(root)
    root.mainloop()
