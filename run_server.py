from tools.FTP.ftp_server import FTPServer

if __name__ == "__main__":
    server = FTPServer()
    server.start_accepting()