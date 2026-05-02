import scapy.all as scapy
from scapy.layers.l2 import ARP, Ether

class ArpSpoofingDetector:
    def __init__(self,):  
        self.devices = dict() # ip to mac
        
    def network_scan(self,ip_range, callback): # 10.100.102.1/24 - 24 is subnet mask -- network scan
        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
    
        result = scapy.srp(packet, timeout=3,verbose=False)[0] # srp returns 2 lists answered and unanswered

        if result:
            self.devices = dict() # ip to mac
            for sent, recieved in result:
                ip = recieved.psrc
                mac = recieved.hwsrc
                self.devices[ip] = mac
            callback(f"network devices: {self.devices}")
        return self.devices
    


    def arp_spoofing_sniffer(self, interface, stop_event, callback):
        scapy.sniff(iface=interface, store=False, prn=lambda packet: self.identify_packet(packet, callback), stop_filter=lambda p: stop_event.is_set())

    def identify_packet(self,packet, callback):
        if packet.haslayer(ARP) and packet[ARP].op == 2:
            sender_ip = packet[ARP].psrc
            sender_mac = packet[ARP].hwsrc
            victim_ip = packet[ARP].pdst
            if sender_ip in self.devices.keys():
                if self.devices[sender_ip] != sender_mac:
                    callback(f"ip: {sender_ip} is being spoofed - idetnifies as a different mac\nvictim: {victim_ip}")
            else:
                callback(f"unknown ip: {sender_ip}")  




