import socket
import threading
import os

class FTPServer: #protocol - send command(get,or send), send file name, file size, file content
    def __init__(self,addr: str, port: int):
        self.server = socket.socket()
        self.FOLDER =  "C:/Users/Alex/Documents/.vscode/python_code/UploadAndDownloadSystem/files"
        self.server.bind((addr,port))
        self.server.listen()

    def start_accepting(self):
        while True:
            self.con, self.addr = self.server.accept()
            thread = threading.Thread(target=self.handling_client,args=(self.con,self.addr))
            print('\n'+thread.name)
            thread.start()
    
    def recvline(self, sock: socket.socket) -> str:
        data =b""
        while not data.endswith(b"\n"):
            part = sock.recv(1)
            if not part:break
            data += part
        return data.decode().strip()

    def upload_to_server(self,con: socket.socket, filename: str):
        size = int(self.recvline(con))
        print("size:",size,"bytes")
        
        filepath = os.path.join(self.FOLDER,filename)
        if os.path.exists(filepath):
            print("file already exists")
            return
        
        received =0
        with open(filepath,"wb") as file:
            while received < size:
                data = con.recv(min(1024, size - received))
                if not data:
                    print("client disconnected")
                    return
                file.write(data)
                received += len(data)
                # print(f"Receiving... {received}/{size} bytes", end="\r") files arent big enough for this
        print("file recieved succesfully")

    def download_from_server(self, con: socket.socket, filename: str):
        filepath = os.path.join(self.FOLDER, filename)
        if not os.path.exists(filepath):
            print("file doesnt exist in folder")
            con.sendall(b"error\n")
        size = str(os.path.getsize(filepath))
        con.sendall((size+"\n").encode())
        with open(filepath, 'rb') as f:
            while data := f.read(1024): # walrus operator, data equals the 1024 bytes from the file(or less) and simuntaniusly returns if data is empty
                con.sendall(data)
        print("file sent")
    
    def handling_client(self, con: socket.socket ,client_addr: str):
        print("connected by", client_addr)

        while True:
            command = self.recvline(con)
            print("command:",command)

            filename = self.recvline(con)
            print("file name:",filename)

            if command == "UPLOAD":
                self.upload_to_server(con, filename)
            elif command == "DOWNLOAD":  
                self.download_from_server(con,filename=filename)
            elif command == "END":
                break
        con.close()

    def __del__(self):
        print("server closing")
        self.server.close()

# server = Server('0.0.0.0', 5000)
# server.start_accepting()



