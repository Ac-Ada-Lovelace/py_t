import socket

def start_tcp_server(host='0.0.0.0', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print("received")

if __name__ == "__main__":
    start_tcp_server()