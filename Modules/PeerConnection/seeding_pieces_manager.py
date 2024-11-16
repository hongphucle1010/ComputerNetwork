import socket
import threading
import os


class SeedingPiecesManager:
    def __init__(self, torrent_manager):
        self.torrent_manager = torrent_manager
        self.stop_trigger = threading.Event()
        self.thread = None
        self.client_threads = []  # Track client-handling threads

    def handle_client(self, client_socket):
        try:
            file_name = client_socket.recv(1024).decode("utf-8")
            print(f"Received request for file: {file_name}")

            # Simulate finding the file in the seeding directory
            seeding_directory = "pieces"
            file_path = os.path.join(seeding_directory, file_name)
            print(f"Looking for file: {file_path}")

            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    client_socket.sendall(file_data)
                print(f"Sent file {file_name} to the peer.")
            else:
                client_socket.sendall(b"ERROR: File not found")
                print(f"File {file_name} not found.")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def startServer(self, port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("localhost", port))
            server_socket.listen(5)
            print("Server is listening on port", port)
            server_socket.settimeout(1)  # Allow periodic checks of stop_trigger
            while not self.stop_trigger.is_set():
                try:
                    client_socket, address = server_socket.accept()
                    print("Connection from", address)
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket,)
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)  # Track the thread
                except socket.timeout:
                    continue
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            server_socket.close()

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            print("Server is already running.")
            return
        print("Starting seeding pieces manager...")
        self.thread = threading.Thread(
            target=self.startServer, args=(self.torrent_manager.program.configs.port,)
        )
        self.thread.start()

    def stop(self):
        if self.thread is None or not self.thread.is_alive():
            print("Server is not running.")
            return
        print("Stopping seeding pieces manager...")

        # Signal the server loop to stop
        self.stop_trigger.set()

        # Wait for the server thread to complete
        self.thread.join()

        # Wait for all client-handling threads to complete
        for client_thread in self.client_threads:
            client_thread.join()

        print("Seeding pieces manager stopped.")

    def seedPieces(self, pieces):
        print("Seeding pieces...")
