import socket
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
import random
import os
import pygame 


class BettingClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Betting Game Client")
        self.root.configure(bg='black')

        self.rotation_limit = 360  # Defina o limite de rotação em graus
        self.rotation_step = 10    # Defina o passo de rotação
        self.rotation_interval = 1000  
        
        self.stopped = False

        #pygame.mixer.init()
        #self.play_music()


        # Load background image for the client window
        self.bg_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\background.png"
        self.bg_image = Image.open(self.bg_image_path)
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
        self.angle = 0  # Initial angle of rotation
        self.vertical_offset = 0  # Vertical offset for the waving effect
        self.direction = 1  # Direction of vertical movement
        self.plane_speed = 5  # Speed of horizontal movement
        self.p1_speed = 5  # Speed of horizontal movement

        self.setup_ui()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 9999))

        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.receiver_thread.start()
        self.client.send("BALANCE|".encode())

        self.rotating = False  # Flag to control rotation

    def setup_ui(self):
        label_font = ('Verdana', 14, 'bold')
        button_font = ('Verdana', 16, 'bold')
        entry_font = ('Verdana', 16)

        # Load and set the image for the exit button
        self.exit_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\x.jpg"
        self.exit_image = Image.open(self.exit_image_path)
        self.exit_image = self.exit_image.resize((40, 40), Image.LANCZOS)  # Resize image if necessary
        self.exit_photo = ImageTk.PhotoImage(self.exit_image)

        # Add exit button with image
        self.exit_button = tk.Button(self.root, image=self.exit_photo, command=self.exit_application, 
                                     bd=0, highlightthickness=0, highlightcolor="#1f6eb1", activebackground="#1f6eb1")
        self.exit_button.place(relx=0.96, rely=0.026, anchor='ne')  # Move to the top-right corner with some padding


        # Balance display
        self.balance_label = tk.Label(self.root, text=f"{self.balance_var.get()}€", fg='white', bg='#013d6f', font=label_font)
        self.balance_label.pack(pady=10)
        self.balance_label.place(relx=0.6, rely=0.242, anchor='center')

        # Previous multipliers frame
        self.multipliers_frame = tk.Frame(self.root)
        self.multipliers_frame.pack(pady=10)
        self.multipliers_frame.place(relx=0.5, rely=0.2755, anchor='center')

        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='white', bg='white', font=label_font)
            lbl.pack(side=tk.LEFT, padx=5)

        # Load background image for the canvas
        self.canva_image_path = "C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\canva.png"  # Replace with your image path
        self.canva_image = Image.open(self.canva_image_path)
        self.canva_photo = ImageTk.PhotoImage(self.canva_image)

        # Canvas with the background image
        self.canvas = tk.Canvas(self.root, width=self.canva_photo.width(), height=self.canva_photo.height(), highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4465, anchor='center')  # Centered in the window

        # Add background image to the canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.canva_photo)

        # Load and display plane image
        self.plane_image = Image.open("C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\p2.png")
        self.plane_image = self.plane_image.resize((100, 100), Image.LANCZOS)
        self.plane_photo = ImageTk.PhotoImage(self.plane_image)
        self.plane_id = self.canvas.create_image(50,180, image=self.plane_photo)  # Centered in the canvas

         # Load and display plane image
        self.p1_image = Image.open("C:\\Users\\igorl\\Documents\\Redes 2ee\\Projeto2\\aqui_Igor\\p1.png")
        self.p1_image = self.p1_image.resize((200, 200), Image.LANCZOS)
        self.p1_photo = ImageTk.PhotoImage(self.p1_image)
        self.p1_id = self.canvas.create_image(350, 170, image=self.p1_photo)  # Centered in the canvas

        # Current multiplier display
        self.current_multiplier_label = tk.Label(self.root, textvariable=self.multiplier_var, fg='black', bg='#edbd46' , font=('Verdana', 20, 'bold', 'italic'))
        self.current_multiplier_label.pack(pady=20)
        self.current_multiplier_label.place(relx=0.5, rely=0.68, anchor='center')

        # Bet input and buttons
  
        self.bet_entry = tk.Entry(self.root, textvariable=self.bet_amount_var, font=entry_font, width=10)
        self.bet_entry.place(relx=0.2, rely=0.765)
 
         # Load image for the bet button
        self.bet_image = Image.open(r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\b1.jpg")
        self.bet_photo = ImageTk.PhotoImage(self.bet_image)

        # Configure bet button with initial image and no border
        self.bet_button = tk.Button(
            self.root, 
            text="BET", 
            image=self.bet_photo, 
            command=self.place_bet,
            bd=0,  # Remove border
            highlightthickness=0,  
            highlightcolor="#1f6eb1", activebackground="#1f6eb1",
            relief='flat',  # Flat appearance
            bg='#216ead'  # Default background color
        )
        self.bet_button.place(relx=0.557, rely=0.75)



        self.cashout_image = Image.open(r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\co1.jpg")
        self.cashout_photo = ImageTk.PhotoImage(self.cashout_image)



        self.cashout_button = tk.Button(self.root, text="CASH OUT",image=self.cashout_photo, command=self.cash_out,  bd=0, 
            highlightthickness=0,
            highlightcolor="#1f6eb1", activebackground="#1f6eb1",
            relief='flat', 
            bg='#216ead'
        )
        self.cashout_button.place(relx=0.5, rely=0.888, anchor='center')

        # Status label
        #self.status_label = tk.Label(self.root, text="Wait for the next round", fg='red', bg='black', font=label_font)
        #self.status_label.pack(pady=10)
        #self.status_label.place(relx=0.5, rely=0.982, anchor='center')



    def exit_application(self):
        self.root.destroy()  # Fecha a janela Tkinter
        pygame.mixer.music.stop()  # Para a música ao sair
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
        self.canvas.coords(self.p1_id, 350, vertical_position)

        self.canvas.tag_raise(self.p1_id, self.plane_id)



    def reset_plane_position(self):
        self.canvas.coords(self.plane_id, 50, 180)

    def place_bet(self):
        bet_amount = self.bet_amount_var.get()
        if bet_amount:
            self.client.send(f"BET {bet_amount}|".encode())
            self.has_bet = True  # Definir como True quando uma aposta for feita
            # Simular a desativação do botão
            self.bet_button.config(
                state=tk.DISABLED, 
                bg='#216ead',  # Mudar a cor de fundo quando desativado
                image=self.bet_photo  # Manter a mesma imagem
            )
            self.cashout_button.config(state=tk.NORMAL)

    def enable_bet_button(self):
        self.bet_button.config(
            state=tk.NORMAL, 
            bg='#216ead'  # Cor do fundo para o botão ativo
        )

    def play_music(self):
        # Carrega e reproduz a música em loop
        music_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\background_music.mp3"  # Caminho para o arquivo de música
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # O argumento -1 faz a música tocar em loop
        else:
            print("Arquivo de música não encontrado.")

    def cash_out(self):
        if self.has_bet:  # Verificar se uma aposta foi feita antes de permitir o cashout
            current_multiplier = float(self.multiplier_var.get().replace('x', ''))
            bet_amount = self.bet_amount_var.get()
            if bet_amount:
                self.client.send(f"CASHOUT {current_multiplier} {bet_amount}|".encode())
                self.cashout_button.config(state=tk.DISABLED)
                self.has_bet = False  # Resetar após o cashout

    def update_previous_multipliers(self):
        for widget in self.multipliers_frame.winfo_children():
            widget.destroy()
        for multiplier in self.previous_multipliers:
            lbl = tk.Label(self.multipliers_frame, text=f"{multiplier:.2f}x", fg='black', bg='white', font=('Arial', 11, 'bold', 'italic'))
            lbl.pack(side=tk.LEFT, padx=5)

    def close_connection(self):
            self.client.close()
            

if __name__ == "__main__":
    root = tk.Tk()
    client = BettingClient(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (client.close_connection(), root.destroy()))
    root.mainloop()