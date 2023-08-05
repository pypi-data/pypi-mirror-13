import socket
import threading


class TcpBlackhole:
    def __init__(self, host='localhost', port=9876, echoFlag=False, debugFlag=False):
        """Assign all the variables provided"""
        self.host = host
        self.port = port
        self.echo = echoFlag
        self.debug = debugFlag
        self.running = False

    def start(self):
        """Bind the server and start listening for connections"""
        server = socket.socket()
        try:
            server.bind((self.host, int(self.port)))
        except ValueError as e:
            print('Error: Could not bind to port. Verify the host and port values are correct.')
            exit(1)
        except OverflowError as e:
            print('Error: Port number must be 0-65535')
            exit(1)
        except OSError as e:
            print('Error: Address already in use. If recently exited, wait a few moments and try again.')
            exit(1)

        server.listen(5)
        self.running = True
        print('Now listening. CTRL-C to end.')

        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(self.running, client))
            client_handler.start()

    def handle_client(self, running, client_socket):
        """Handle the client, read and discard until the client terminates the connection."""
        request_data = client_socket.recv(4096)
        while request_data and running:
            if self.echo:
                client_socket.send(request_data)
            if self.debug:
                print(request_data)
            request_data = client_socket.recv(4096)
        client_socket.close()
