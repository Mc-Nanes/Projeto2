import socket

# Função para obter o endereço IP local do servidor
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não precisa realmente enviar dados
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Configurações do cliente
SERVER_HOST = get_local_ip()  # Endereço IP do servidor detectado automaticamente
SERVER_PORT = 8080            # Porta a ser utilizada

# Função para enviar uma requisição GET
def send_get_request(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        request = f'GET {path} HTTP/1.1\r\nHost: {SERVER_HOST}\r\n\r\n'
        client_socket.sendall(request.encode())
        
        response = b''
        while True:
            part = client_socket.recv(1024)
            if not part:
                break
            response += part
        
        print(response.decode())

# Enviar requisição GET para o arquivo index.html
send_get_request('/')
