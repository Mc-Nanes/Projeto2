# start_game.py
import subprocess
import time
import os

# Define o caminho absoluto para os scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
server_script = os.path.join(script_dir, "aqui_Igor", "servidor.py")
client_script = os.path.join(script_dir, "aqui_Igor", "main_menu.py")

# Função para iniciar o servidor
def start_server():
    return subprocess.Popen(["python", server_script])

# Função para iniciar o cliente
def start_client():
    subprocess.Popen(["python", client_script])

if __name__ == "__main__":
    # Inicia o servidor
    server_process = start_server()
    
    # Aguarda um pouco para garantir que o servidor esteja iniciado
    time.sleep(5)  # Ajuste o tempo se necessário
    
    # Inicia o cliente
    start_client()
    
    # Mantém o script em execução para que o servidor continue rodando
    server_process.wait()
