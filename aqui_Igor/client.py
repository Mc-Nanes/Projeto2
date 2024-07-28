import socket
import threading
import tkinter as tk
from tkinter import messagebox
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
        self.client.send("BALANCE|".encode())

    def setup_ui(self):
        label_font = ('Arial', 14, 'bold')
        button_font = ('Arial', 16, 'bold')
        entry_font = ('Arial', 16)

        # Balance display
        self.balance_label = tk.Label(self.root, text=f"BALANCE: {self.balance_var.get()}€", fg='#00FF00', bg='black', font=label_font)
        self.balance_label.pack(pady=10)

        # Previous multipliers frame
        self.multipliers_frame = tk.Frame(self.root, bg='black')
        self.multipliers_frame.pack(pady=10)

        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='#00FFFF', bg='black', font=label_font)
            lbl.pack(side=tk.LEFT, padx=5)

        # Canvas with plane image
        self.canvas = tk.Canvas(self.root, width=500, height=250, bg='black', highlightthickness=0)
        self.canvas.pack(pady=20)
        self.plane_image = Image.open("aqui_Igor/plane.png")
        self.plane_image = self.plane_image.resize((50, 50), Image.LANCZOS)
        self.plane_photo = ImageTk.PhotoImage(self.plane_image)
        self.plane_id = self.canvas.create_image(50, 125, image=self.plane_photo)

        # Current multiplier display
        self.current_multiplier_label = tk.Label(self.root, textvariable=self.multiplier_var, fg='white', bg='black', font=('Arial', 32, 'bold'))
        self.current_multiplier_label.pack(pady=20)

        # Bet input and buttons
        self.bet_frame = tk.Frame(self.root, bg='black')
        self.bet_frame.pack(pady=10)
        self.bet_entry = tk.Entry(self.bet_frame, textvariable=self.bet_amount_var, font=entry_font, width=10)
        self.bet_entry.pack(side=tk.LEFT, padx=10)
        self.bet_button = tk.Button(self.bet_frame, text="BET", bg='#FF007F', fg='white', font=button_font, command=self.place_bet)
        self.bet_button.pack(side=tk.LEFT, padx=10)

        self.cashout_button = tk.Button(self.root, text="CASH OUT", bg='#FF007F', fg='white', font=button_font, command=self.cash_out, state=tk.DISABLED)
        self.cashout_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="Wait for the next round", fg='red', bg='black', font=label_font)
        self.status_label.pack(pady=10)

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
            self.update_plane_position(float(multiplier))
        elif message == "STOPPED":
            self.reset_plane_position()
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
            self.balance_label.config(text=f"BALANCE: {self.balance_var.get()}€")
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

    def update_plane_position(self, multiplier):
        new_x = multiplier * 50
        if new_x > self.canvas.winfo_width():
            new_x = new_x % self.canvas.winfo_width()  # Loop back to the start
        self.canvas.coords(self.plane_id, new_x, 125)

    def reset_plane_position(self):
        self.canvas.coords(self.plane_id, 50, 125)

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
        for widget in self.multipliers_frame.winfo_children():
            widget.destroy()
        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='#00FFFF', bg='black', font=('Arial', 12, 'bold'))
            lbl.pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    client = BettingClient(root)
    root.mainloop()
