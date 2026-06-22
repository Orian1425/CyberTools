import os
import psutil

SERVER_IP = '0.0.0.0'
PORTS = {
    "FTP": 5005,
    "RDP": 7777,
    "Broadcast": 50001
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_STORAGE = os.path.join(BASE_DIR, "storage", "ftp_server_storage")
if not os.path.exists(SERVER_STORAGE):
    os.makedirs(SERVER_STORAGE)

KEYLOGGER_DESTINATION = os.path.join(BASE_DIR, "storage", "keylog.txt")



# --- VirusTotal Settings ---
VT_API_KEY = "api key"


# --- Networking Settings ---
def get_interfaces():
    """Returns a list of available network interface names."""
    return list(psutil.net_if_addrs().keys())

# --- UI Settings ---
APPEARANCE_MODE = "dark"
DEFAULT_COLOR_THEME = "blue"
WINDOW_SIZE = "700x500"
