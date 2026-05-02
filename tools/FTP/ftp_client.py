import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox


class FTPClient:
    def __init__(self,host_ip: str, host_port: int):  
        self.is_connected = False
        self.error_message = ""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(3)
            self.client.connect((host_ip, host_port))
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            self.error_message = str(e)
        
    def recvline(self, sock: socket.socket) -> str:
        data =b""
        while not data.endswith(b"\n"):
            part = sock.recv(1)
            if not part:break
            data += part
        return data.decode().strip()

    def download_file_to_client(self, filename: str): 
        try:
            command = b"DOWNLOAD\n"
            self.client.sendall(command)
            self.client.sendall((filename + '\n').encode())
            
            # Handshake
            status = self.recvline(self.client)
            if status.startswith("ERROR"):
                return status
            
            # If OK, server sends size next
            temp = self.recvline(self.client)
            if not temp:
                return "ERROR: Server disconnected"
            size = int(temp)
            
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_folder, exist_ok=True)
            filepath = os.path.join(downloads_folder, filename)

            received = 0
            with open(filepath,"wb") as f:
                while received < size:
                    data = self.client.recv(min(1024, size - received))
                    if not data: break
                    f.write(data)
                    received += len(data)

            return "DOWNLOAD_SUCCESS"
        except Exception as e:
            return f"ERROR: {str(e)}"
        finally:
            self.end_connection()
        
    def upload_file_to_server(self, filepath: str):
        if not filepath:
            return "NO_FILE_SELECTED"
        try:
            filename = os.path.basename(str(filepath))
            size = str(os.path.getsize(filepath))
            
            self.client.sendall(b"UPLOAD\n")
            self.client.sendall((filename + '\n').encode())
            self.client.sendall((size + '\n').encode())

            # Handshake
            status = self.recvline(self.client)
            if status != "OK":
                return status # Returns ERROR: <msg>

            with open(filepath, 'rb') as f:
                while data := f.read(1024):
                    self.client.sendall(data)
            return "UPLOAD_SUCCESS"
        except Exception as e:
            return f"ERROR: {str(e)}"
        finally:
            self.end_connection()

    def end_connection(self):
        command = b"END\n"
        self.client.sendall(command)
        self.client.close()

