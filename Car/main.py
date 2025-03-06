import socket

def start_server(host='localhost', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f'Server listening on {host}:{port}')

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f'Connected by {client_address}')
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print(f'Received message: {data.decode()}')

if __name__ == '__main__':
    '''
    add a car first, then with the port given from the backend establish a connection with the CLI app
    '''
    start_server(port=39689) # port number from the car (hardcoded for now)