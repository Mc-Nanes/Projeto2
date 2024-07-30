import socket
import threading
import os

# Função para obter o endereço IP local
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

# Configurações do servidor
HOST = get_local_ip()  # Endereço IP do servidor detectado automaticamente
PORT = 8080            # Porta a ser utilizada

# Mapear extensões de arquivo para tipos MIME
MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp'
}

# Função para ler arquivos e retornar seu conteúdo e tipo MIME
def read_file(file_path):
    ext = os.path.splitext(file_path)[1]
    mime_type = MIME_TYPES.get(ext, 'application/octet-stream')
    try:
        with open(file_path, 'rb') as f:
            return f.read(), mime_type
    except FileNotFoundError:
        return None, None

# Função para lidar com requisições HTTP
def handle_request(request):
    headers = request.split('\n')
    first_line = headers[0].split()
    if len(first_line) < 2:
        return 'HTTP/1.1 400 Bad Request\n\nBad Request'.encode()

    method = first_line[0]
    path = first_line[1]

    if method != 'GET':
        return 'HTTP/1.1 405 Method Not Allowed\n\nMethod Not Allowed'.encode()

    if path == '/':
        path = '/index.html'
    
    file_content, mime_type = read_file('.' + path)
    if file_content is None:
        return 'HTTP/1.1 404 Not Found\n\nNot Found'.encode()

    response = f'HTTP/1.1 200 OK\nContent-Type: {mime_type}\n\n'.encode() + file_content
    return response

def client_thread(client_socket):
    request = client_socket.recv(1024).decode()
    response = handle_request(request)
    client_socket.sendall(response)
    client_socket.close()

# Criar e configurar o socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Servidor rodando em http://{HOST}:{PORT}')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Conexão de {client_address}')
        threading.Thread(target=client_thread, args=(client_socket,)).start()
