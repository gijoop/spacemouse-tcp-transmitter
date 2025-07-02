import socket

TCP_IP = '0.0.0.0'
TCP_PORT = 5005

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((TCP_IP, TCP_PORT))
        server_socket.listen(1)
        print(f"TCP server listening on {TCP_IP}:{TCP_PORT}")

        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received:", data.decode("utf-8"))

if __name__ == "__main__":
    start_server()
