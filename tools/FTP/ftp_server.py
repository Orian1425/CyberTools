import socket
import threading
import os
import config # ייבוא ההגדרות

class FTPServer:
    def __init__(self, addr=config.HOST_IP, port=config.DEFAULT_PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # מאפשר הרצה מחדש מהירה
        self.folder = config.SERVER_STORAGE
        
        try:
            self.server.bind((addr, port))
            self.server.listen()
            print(f"[*] Server listening on {addr}:{port}")
            print(f"[*] Storage folder: {self.folder}")
        except Exception as e:
            print(f"[!] Bind failed: {e}")

    def start_accepting(self):
        """הפעלת לולאת קבלת לקוחות"""
        try:
            while True:
                con, addr = self.server.accept()
                thread = threading.Thread(target=self.handling_client, args=(con, addr))
                thread.daemon = True # מבטיח שה-Thread ייסגר כשהתוכנה הראשית נסגרת
                thread.start()
        except KeyboardInterrupt:
            print("\n[!] Server stopping...")
        finally:
            self.stop_server()

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
            
            received = 0
            with open(filepath, "wb") as file:
                while received < size:
                    data = con.recv(min(1024, size - received))
                    if not data: break
                    file.write(data)
                    received += len(data)
            print(f"[+] File '{filename}' received successfully.")
        except Exception as e:
            print(f"[!] Upload error: {e}")

    def download_from_server(self, con: socket.socket, filename: str):
        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            print(f"[!] File '{filename}' not found.")
            con.sendall(b"0\n") # שליחת גודל 0 כסימן לשגיאה
            return

        size = os.path.getsize(filepath)
        con.sendall((str(size) + "\n").encode())
        
        with open(filepath, 'rb') as f:
            while data := f.read(1024):
                con.sendall(data)
        print(f"[+] File '{filename}' sent to client.")

    def handling_client(self, con: socket.socket, client_addr: str):
        print(f"[*] New connection from {client_addr}")
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
        except Exception as e:
            print(f"[!] Client {client_addr} error: {e}")
        finally:
            con.close()
            print(f"[*] Connection with {client_addr} closed.")

    def stop_server(self):
        """סגירה מסודרת של השרת"""
        print("[*] Server closing...")
        self.server.close()