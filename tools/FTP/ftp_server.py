import time
import socket
import threading
import os
import config # ייבוא ההגדרות

class FTPServer:
    def __init__(self, log_callback, addr=config.SERVER_IP, port=config.PORTS["FTP"]):
        self.log = log_callback
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.folder = config.SERVER_STORAGE
        
        self.broadcast_stop_event = threading.Event()
        
        try:
            broadcast_port = config.PORTS["Broadcast"]
            self.broadcast_presence_thread = threading.Thread(
                target=broadcast_presence,
                args=(self.broadcast_stop_event, broadcast_port),
                daemon=True
            )
            self.broadcast_presence_thread.start()

            self.server.bind((addr, port))
            self.server.listen()
            self.log(f"[*] Server listening on {addr}:{port}")
            self.log(f"[*] Storage folder: {self.folder}")
        except Exception as e:
            self.log(f"[!] Bind failed: {e}")

    def send_response(self, con, msg):
        con.sendall((msg + "\n").encode())

    def start_accepting(self, stop_event: threading.Event):
        """Start the client acceptance loop with stop event support"""
        self.server.settimeout(1.0) # 1 second timeout to allow checking stop_event
        self.log(f"[*] FTP Server started on {self.server.getsockname()[0]}:{self.server.getsockname()[1]}\n")
        
        try:
            while not stop_event.is_set():
                try:
                    con, addr = self.server.accept()
                    thread = threading.Thread(target=self.handling_client, args=(con, addr))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if not stop_event.is_set():
                        self.log(f"[!] Accept error: {e}")
                    break
        finally:
            self.stop_server()

    def handling_client(self, con: socket.socket, client_addr):
        self.log(f"[*] New connection from {client_addr}")
        try:
            while True:
                command = self.recvline(con)
                if not command or command == "END":
                    break
                
                filename = self.recvline(con)
                if not filename: break

                if command == "UPLOAD":
                    self.upload_to_server(con, filename)
                elif command == "DOWNLOAD":
                    self.download_from_server(con, filename)
                else:
                    self.send_response(con, "ERROR: Invalid command")
                    break
        except Exception as e:
            self.log(f"[!] Client {client_addr} error: {e}")
        finally:
            con.close()
            self.log(f"[*] Connection with {client_addr} closed.\n")

    def recvline(self, sock: socket.socket) -> str:
        data = b""
        while not data.endswith(b"\n"):
            part = sock.recv(1)
            if not part: break
            data += part
        return data.decode().strip()

    def upload_to_server(self, con: socket.socket, filename: str):
        try:
            size_data = self.recvline(con)
            if not size_data: return
            size = int(size_data)
            
            filepath = os.path.join(self.folder, filename)
            
            # Check for file locks/permissions before accepting data
            try:
                file = open(filepath, "wb")
            except PermissionError:
                self.log(f"[!] Permission denied: '{filename}' (is it open elsewhere?)")
                self.send_response(con, "ERROR: Permission denied")
                return
            except Exception as e:
                self.log(f"[!] Error opening '{filename}': {e}")
                self.send_response(con, f"ERROR: {str(e)}")
                return

            self.send_response(con, "OK") # Tell client we are ready

            received = 0
            with file:
                while received < size:
                    data = con.recv(min(1024, size - received))
                    if not data: break
                    file.write(data)
                    received += len(data)
            self.log(f"[+] File '{filename}' received successfully.")
        except Exception as e:
            self.log(f"[!] Upload error: {e}")

    def download_from_server(self, con: socket.socket, filename: str):
        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            self.log(f"[!] File '{filename}' not found.")
            self.send_response(con, "ERROR: File not found")
            return

        try:
            size = os.path.getsize(filepath)
            with open(filepath, 'rb') as f:
                self.send_response(con, "OK")
                self.send_response(con, str(size))
                
                while data := f.read(1024):
                    con.sendall(data)
            self.log(f"[+] File '{filename}' sent to client.")
        except Exception as e:
            self.log(f"[!] Download error: {e}")
            self.send_response(con, f"ERROR: {str(e)}")

    def stop_server(self):
        """Graceful server shutdown"""
        self.log("[*] FTP Server stopped.\n")
        self.broadcast_stop_event.set()
        self.server.close()


def broadcast_presence(stop_event: threading.Event, broadcast_port: int):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Unique token so your client knows it's actually your server
    magic_token = b"Orian" 
    
    print(f"Broadcasting server presence to the LAN on port {broadcast_port}...")
    try:
        while not stop_event.is_set():
            # Broadcast the token to everyone on the local subnet
            sock.sendto(magic_token, ('<broadcast>', broadcast_port))
            for _ in range(30):
                if stop_event.is_set():
                    break
                time.sleep(0.1)
    except Exception as e:
        print(f"Stopping broadcast due to: {e}")
    finally:
        sock.close()