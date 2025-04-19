import socket

# send message to 121.195.169.252:9527
def send_message(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(message.encode())
        response = s.recv(1024)
        print('Received:', response.decode())

# Example usage
send_message('121.195.169.252', 9527, 'Hello, Server!')

