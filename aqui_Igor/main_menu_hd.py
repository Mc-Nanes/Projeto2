import tkinter as tk
from PIL import Image, ImageTk
from client import BettingClient  # Certifique-se de que o caminho está correto

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.scale_factor = 0.5  # Defina o fator de escala para 50%
        self.root.title("Main Menu")
        
        # Load background image for the window
        self.bg_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\menu.png"
        self.bg_image = Image.open(self.bg_image_path)
        self.bg_image = self.bg_image.resize(
            (int(self.bg_image.width * self.scale_factor), int(self.bg_image.height * self.scale_factor)), 
            Image.LANCZOS
        )
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Set window size to image size and disable resizing
        self.root.geometry(f"{self.bg_photo.width()}x{self.bg_photo.height()}")
        self.root.resizable(False, False)

        # Create a label to hold the image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)  # Make the image fill the window

        # Load and set the image for the play button
        self.play_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\jogar.jpg"
        self.play_image = Image.open(self.play_image_path)
        self.play_image = self.play_image.resize(
            (int(203 * self.scale_factor), int(75 * self.scale_factor)), 
            Image.LANCZOS
        )
        self.play_photo = ImageTk.PhotoImage(self.play_image)

        # Add play button with image
        self.play_button = tk.Button(
            self.root, 
            command=self.start_game, 
            image=self.play_photo, 
            bd=0, 
            highlightthickness=0, 
            highlightcolor="#1f6eb1", 
            activebackground="#1f6eb1"
        )
        self.play_button.place(relx=0.5, rely=0.882, anchor='center')  # Move the button further down

        # Load and set the image for the exit button
        self.exit_image_path = r"C:\Users\igorl\Documents\Redes 2ee\Projeto2\aqui_Igor\x.jpg"
        self.exit_image = Image.open(self.exit_image_path)
        self.exit_image = self.exit_image.resize(
            (int(40 * self.scale_factor), int(40 * self.scale_factor)), 
            Image.LANCZOS
        )
        self.exit_photo = ImageTk.PhotoImage(self.exit_image)

        # Add exit button with image
        self.exit_button = tk.Button(
            self.root, 
            image=self.exit_photo, 
            command=self.root.quit, 
            bd=0, 
            highlightthickness=0, 
            highlightcolor="#1f6eb1", 
            activebackground="#1f6eb1"
        )
        self.exit_button.place(relx=0.96, rely=0.026, anchor='ne')  # Move to the top-right corner with some padding

    def start_game(self):
        # Get the position of the main window
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        # Get the dimensions of the main window
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Destroy the main menu window
        self.root.destroy()

        # Create a new root window for the BettingClient
        client_root = tk.Tk()
        client_root.title("Betting Game Client")

        # Set the position of the new window to be the same as the previous window
        client_root.geometry(f"{width}x{height}+{x}+{y}")

        # Initialize BettingClient with the new window
        BettingClient(client_root)
        client_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()
