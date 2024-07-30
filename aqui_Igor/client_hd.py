import socket
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
import random
import os

class BettingClient:
    def __init__(self, root):
        self.root = root
        self.scale_factor = 0.5  # Defina o fator de escala para 50%
        self.root.title("Betting Game Client")
        self.root.configure(bg='black')

        self.rotation_limit = 360
        self.rotation_step = 10
        self.rotation_interval = 1000
        
        self.stopped = False

        # Load background image for the client window
        self.bg_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\background.png"
        self.bg_image = Image.open(self.bg_image_path)
        self.bg_image = self.bg_image.resize((int(self.bg_image.width * self.scale_factor), int(self.bg_image.height * self.scale_factor)), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry(f"{self.bg_photo.width()}x{self.bg_photo.height()}")
        self.root.resizable(False, False)

        # Create a label to hold the background image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)  # Make the image fill the window

        self.balance_var = tk.StringVar(value="0.00")
        self.multiplier_var = tk.StringVar(value="1.00x")
        self.bet_amount_var = tk.StringVar(value="")
        self.previous_multipliers = []
        self.angle = 0
        self.vertical_offset = 0
        self.direction = 1
        self.plane_speed = 5
        self.p1_speed = 5

        self.setup_ui()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 9999))

        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.receiver_thread.start()
        self.client.send("BALANCE|".encode())

        self.rotating = False

    def setup_ui(self):
        label_font_size = int(14 * self.scale_factor)
        button_font_size = int(16 * self.scale_factor)
        entry_font_size = int(16 * self.scale_factor)

        label_font = ('Verdana', label_font_size, 'bold')
        button_font = ('Verdana', button_font_size, 'bold')
        entry_font = ('Verdana', entry_font_size)

        # Load and set the image for the exit button
        self.exit_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\x.jpg"
        self.exit_image = Image.open(self.exit_image_path)
        self.exit_image = self.exit_image.resize((int(40 * self.scale_factor), int(40 * self.scale_factor)), Image.LANCZOS)
        self.exit_photo = ImageTk.PhotoImage(self.exit_image)

        # Add exit button with image
        self.exit_button = tk.Button(self.root, image=self.exit_photo, command=self.exit_application, 
                                     bd=0, highlightthickness=0, highlightcolor="#1f6eb1", activebackground="#1f6eb1")
        self.exit_button.place(relx=0.96, rely=0.026, anchor='ne')

        # Balance display
        self.balance_label = tk.Label(self.root, text=f"{self.balance_var.get()}€", fg='white', bg='#013d6f', font=label_font)
        self.balance_label.pack(pady=int(10 * self.scale_factor))
        self.balance_label.place(relx=0.6, rely=0.242, anchor='center')

        # Previous multipliers frame
        self.multipliers_frame = tk.Frame(self.root)
        self.multipliers_frame.pack(pady=int(10 * self.scale_factor))
        self.multipliers_frame.place(relx=0.5, rely=0.2755, anchor='center')

        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='white', bg='white', font=label_font)
            lbl.pack(side=tk.LEFT, padx=int(5 * self.scale_factor))

        # Load background image for the canvas
        self.canva_image_path = "C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\canva.png"
        self.canva_image = Image.open(self.canva_image_path)
        self.canva_image = self.canva_image.resize((int(self.canva_image.width * self.scale_factor), int(self.canva_image.height * self.scale_factor)), Image.LANCZOS)
        self.canva_photo = ImageTk.PhotoImage(self.canva_image)

        # Canvas with the background image
        self.canvas = tk.Canvas(self.root, width=self.canva_photo.width(), height=self.canva_photo.height(), highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4465, anchor='center')

        # Add background image to the canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.canva_photo)

        # Load and display plane image
        self.plane_image = Image.open("C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\p2.png")
        self.plane_image = self.plane_image.resize((int(100 * self.scale_factor), int(100 * self.scale_factor)), Image.LANCZOS)
        self.plane_photo = ImageTk.PhotoImage(self.plane_image)
        self.plane_id = self.canvas.create_image(int(50 * self.scale_factor), int(200 * self.scale_factor), image=self.plane_photo)

        # Load and display p1 image
        self.p1_image = Image.open("C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\p1.png")
        self.p1_image = self.p1_image.resize((int(200 * self.scale_factor), int(200 * self.scale_factor)), Image.LANCZOS)
        self.p1_photo = ImageTk.PhotoImage(self.p1_image)
        self.p1_id = self.canvas.create_image(int(350 * self.scale_factor), int(220 * self.scale_factor), image=self.p1_photo)

        # Current multiplier display
        self.current_multiplier_label = tk.Label(self.root, textvariable=self.multiplier_var, fg='black', bg='#edbd46' , font=('Verdana', int(20 * self.scale_factor), 'bold', 'italic'))
        self.current_multiplier_label.pack(pady=int(20 * self.scale_factor))
        self.current_multiplier_label.place(relx=0.5, rely=0.68, anchor='center')

        # Bet input and buttons
        self.bet_entry = tk.Entry(self.root, textvariable=self.bet_amount_var, font=entry_font, width=int(10 * self.scale_factor))
        self.bet_entry.place(relx=0.23, rely=0.765)
 
        # Load image for the bet button
        self.bet_image = Image.open(r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\b1.jpg")
        self.bet_image = self.bet_image.resize((int(150 * self.scale_factor), int(50 * self.scale_factor)), Image.LANCZOS)
        self.bet_photo = ImageTk.PhotoImage(self.bet_image)

        # Configure bet button with initial image and no border
        self.bet_button = tk.Button(
            self.root, 
            text="BET", 
            image=self.bet_photo, 
            command=self.place_bet,
            bd=0, 
            highlightthickness=0,  
            highlightcolor="#1f6eb1", activebackground="#1f6eb1",
            relief='flat',  
            bg='#216ead'  
        )
        self.bet_button.place(relx=0.62, rely=0.76)

        # Load image for the cashout button
        self.cashout_image = Image.open(r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\co1.jpg")
        self.cashout_image = self.cashout_image.resize((int(100 * self.scale_factor), int(50 * self.scale_factor)), Image.LANCZOS)
        self.cashout_photo = ImageTk.PhotoImage(self.cashout_image)

        self.cashout_button = tk.Button(self.root, text="CASH OUT", image=self.cashout_photo, command=self.cash_out, bd=0, 
            highlightthickness=0,
            highlightcolor="#1f6eb1", activebackground="#1f6eb1",
            relief='flat', 
            bg='#216ead'
        )
        self.cashout_button.place(relx=0.5, rely=0.888, anchor='center')

        # Status label (comentado, mas pode ser ativado se necessário)
        #self.status_label = tk.Label(self.root, text="Wait for the next round", fg='red', bg='black', font=label_font)
        #self.status_label.pack(pady=int(10 * self.scale_factor))
        #self.status_label.place(relx=0.5, rely=0.982, anchor='center')

    def exit_application(self):
        self.root.destroy()
        os._exit(0)
      
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
            self.bet_button.config(state=tk.DISABLED)
        elif message.startswith("POSITION"):
            parts = message.split()[1].split(',')
            position = float(parts[0])
            vertical_position = float(parts[1])
            self.update_plane_position(position, vertical_position)
        elif message == "STOPPED":
            self.reset_plane_position()
            multiplier = float(self.multiplier_var.get().replace('x', ''))
            self.previous_multipliers.append(multiplier)
            self.update_previous_multipliers()
            self.bet_button.config(state=tk.NORMAL)
            self.cashout_button.config(state=tk.DISABLED)
        elif message.startswith("WINNINGS"):
            winnings = float(message.split()[1])
            #messagebox.showinfo("Betting Game", f"You won {winnings:.2f}!")
        elif message.startswith("BALANCE"):
            balance = float(message.split()[1])
            self.balance_label.config(text=f"Saldo: R$ {balance:.2f}")
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
        
    def update_plane_position(self, position, vertical_position):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        print(f"Updating plane position to: {position}, {vertical_position}")

        if position < 0:
            position = canvas_width + position
        elif position > canvas_width:
            position = position % canvas_width

        if vertical_position < 0:
            vertical_position = canvas_height + vertical_position
        elif vertical_position > canvas_height:
            vertical_position = vertical_position % canvas_height

        self.canvas.coords(self.plane_id, position, vertical_position)
        self.canvas.coords(self.p1_id, int(350 * self.scale_factor), vertical_position)

        self.canvas.tag_raise(self.p1_id, self.plane_id)

    def reset_plane_position(self):
        self.canvas.coords(self.plane_id, int(50 * self.scale_factor), int(180 * self.scale_factor))
        self.canvas.coords(self.p1_id, int(350 * self.scale_factor), int(220 * self.scale_factor))

    def place_bet(self):
        bet_amount = self.bet_amount_var.get()
        if bet_amount:
            self.client.send(f"BET {bet_amount}|".encode())
            self.has_bet = True
            self.bet_button.config(
                state=tk.DISABLED, 
                bg='#216ead',
                image=self.bet_photo
            )
            self.cashout_button.config(state=tk.NORMAL)

    def enable_bet_button(self):
        self.bet_button.config(
            state=tk.NORMAL, 
            bg='#216ead'
        )

    def cash_out(self):
        if self.has_bet:
            current_multiplier = float(self.multiplier_var.get().replace('x', ''))
            bet_amount = self.bet_amount_var.get()
            if bet_amount:
                self.client.send(f"CASHOUT {current_multiplier} {bet_amount}|".encode())
                self.cashout_button.config(state=tk.DISABLED)
                self.has_bet = False

    def update_previous_multipliers(self):
        for widget in self.multipliers_frame.winfo_children():
            widget.destroy()
        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='black', bg='white', font=('Arial', int(11 * self.scale_factor), 'bold', 'italic'))
            lbl.pack(side=tk.LEFT, padx=int(5 * self.scale_factor))

    def close_connection(self):
        self.client.close()

if __name__ == "__main__":
    root = tk.Tk()
    client = BettingClient(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (client.close_connection(), root.destroy()))
    root.mainloop()
