import customtkinter as ctk
import threading
from tools.Arp_spoofing.arp_spoofing import ArpSpoofing
from tools.Arp_spoofing.arp_spoofing_detector import ArpSpoofingDetector
from tools.Sniffing.sniffer import Sniffer
import config

class NetworkingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label = ctk.CTkLabel(self, text="Networking Tools", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(10, 5))

        # Tabview for different tools
        self.tabview = ctk.CTkTabview(self, height=250)
        self.tabview.pack(pady=5, padx=20, fill="x")

        self.tab_spoofing = self.tabview.add("ARP Spoofing")
        self.tab_detector = self.tabview.add("ARP Detector")
        self.tab_sniffer = self.tabview.add("HTTP Sniffer")

        self._setup_spoofing_tab()
        self._setup_detector_tab()
        self._setup_sniffer_tab()

        # Log box
        self.log_label = ctk.CTkLabel(self, text="Activity Log", font=("Roboto", 16, "bold"))
        self.log_label.pack(pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self, height=200)
        self.log_box.pack(pady=5, padx=20, fill="both", expand=True)

        # Threading events
        self.spoof_stop_event = threading.Event()
        self.detector_stop_event = threading.Event()
        self.sniffer_stop_event = threading.Event()
        
        self.spoof_thread = None
        self.detector_thread = None
        self.sniffer_thread = None

    def log(self, message):
        if self.winfo_exists():
            self.log_box.insert("end", f"> {message}\n")
            self.log_box.see("end")


    # ==========================
    # ARP SPOOFING
    # ==========================
    def _setup_spoofing_tab(self):
        frame = ctk.CTkFrame(self.tab_spoofing, fg_color="transparent")
        frame.pack(pady=10)

        # Inputs
        ctk.CTkLabel(frame, text="Target IP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.spoof_target_entry = ctk.CTkEntry(frame, width=150)
        self.spoof_target_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Gateway IP:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.spoof_gateway_entry = ctk.CTkEntry(frame, width=150)
        self.spoof_gateway_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Attacker IP (Optional):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.spoof_attacker_entry = ctk.CTkEntry(frame, width=150)
        self.spoof_attacker_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        self.spoof_mitm_btn = ctk.CTkButton(btn_frame, text="Start MITM", fg_color="green", hover_color="darkgreen", command=lambda: self.start_spoofing(is_mitm=True))
        self.spoof_mitm_btn.pack(side="left", padx=5)

        self.spoof_dos_btn = ctk.CTkButton(btn_frame, text="Start DoS", fg_color="orange", hover_color="darkorange", command=lambda: self.start_spoofing(is_mitm=False))
        self.spoof_dos_btn.pack(side="left", padx=5)

        self.spoof_stop_btn = ctk.CTkButton(btn_frame, text="Stop", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_spoofing)
        self.spoof_stop_btn.pack(side="left", padx=5)

    def start_spoofing(self, is_mitm):
        target_ip = self.spoof_target_entry.get()
        gateway_ip = self.spoof_gateway_entry.get()
        attacker_ip = self.spoof_attacker_entry.get()

        if not target_ip or not gateway_ip:
            self.log("Error: Target IP and Gateway IP are required.")
            return

        self.spoof_stop_event.clear()
        self.spoof_mitm_btn.configure(state="disabled")
        self.spoof_dos_btn.configure(state="disabled")
        self.spoof_stop_btn.configure(state="normal")
        mode = "MITM" if is_mitm else "DoS"
        self.log(f"Starting ARP Spoofing ({mode})...")

        spoofer = ArpSpoofing()
        self.spoof_thread = threading.Thread(
            target=spoofer.spoof_device, 
            args=(target_ip, gateway_ip, is_mitm, attacker_ip, self.spoof_stop_event, self.log),
            daemon=True
        )
        self.spoof_thread.start()

    def stop_spoofing(self):
        self.log("Stopping ARP Spoofing...")
        self.spoof_stop_event.set()
        self.spoof_mitm_btn.configure(state="normal")
        self.spoof_dos_btn.configure(state="normal")
        self.spoof_stop_btn.configure(state="disabled")

    # ==========================
    # ARP DETECTOR
    # ==========================
    def _setup_detector_tab(self):
        frame = ctk.CTkFrame(self.tab_detector, fg_color="transparent")
        frame.pack(pady=10)

        # Scan Section
        ctk.CTkLabel(frame, text="IP Range (e.g. 192.168.1.1/24):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.detector_range_entry = ctk.CTkEntry(frame, width=150)
        self.detector_range_entry.grid(row=0, column=1, padx=5, pady=5)

        # Sniffer Section
        ctk.CTkLabel(frame, text="Interface:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.detector_interface_dropdown = ctk.CTkOptionMenu(frame, values=config.get_interfaces(), width=150)
        self.detector_interface_dropdown.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)

        self.detector_start_btn = ctk.CTkButton(btn_frame, text="Start Detector", fg_color="green", hover_color="darkgreen", command=self.start_detector)
        self.detector_start_btn.pack(side="left", padx=10)

        self.detector_stop_btn = ctk.CTkButton(btn_frame, text="Stop Detector", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_detector)
        self.detector_stop_btn.pack(side="left", padx=10)

        self.detector_scan_btn = ctk.CTkButton(btn_frame, text="Scan Network", command=self.scan_network)
        self.detector_scan_btn.pack(side="left", padx=10)


        self.detector_instance = ArpSpoofingDetector()

    def scan_network(self):
        ip_range = self.detector_range_entry.get()
        if not ip_range:
            self.log("Error: IP Range is required for scanning.")
            return
        
        self.log(f"Scanning network range: {ip_range}...")
        self.detector_scan_btn.configure(state="disabled")
        
        def run_scan():
            self.detector_instance.network_scan(ip_range, self.log)
            self.log("Network scan complete.\n")
            self.detector_scan_btn.configure(state="normal")

        threading.Thread(target=run_scan, daemon=True).start()

    def start_detector(self):
        interface = self.detector_interface_dropdown.get()
        if not interface:
            self.log("Error: Interface is required for the detector.")
            return

        self.detector_stop_event.clear()
        self.detector_start_btn.configure(state="disabled")
        self.detector_stop_btn.configure(state="normal")
        self.log(f"Starting ARP Spoofing Detector on {interface}...")

        self.detector_thread = threading.Thread(
            target=self.detector_instance.arp_spoofing_sniffer, 
            args=(interface, self.detector_stop_event, self.log),
            daemon=True
        )
        self.detector_thread.start()

    def stop_detector(self):
        self.log("Stopping ARP Spoofing Detector...")
        self.detector_stop_event.set()
        self.detector_start_btn.configure(state="normal")
        self.detector_stop_btn.configure(state="disabled")

    # ==========================
    # HTTP SNIFFER
    # ==========================
    def _setup_sniffer_tab(self):
        frame = ctk.CTkFrame(self.tab_sniffer, fg_color="transparent")
        frame.pack(pady=10)

        ctk.CTkLabel(frame, text="Interface:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.sniffer_interface_dropdown = ctk.CTkOptionMenu(frame, values=config.get_interfaces(), width=150)
        self.sniffer_interface_dropdown.grid(row=0, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, columnspan=2, pady=15)

        self.sniffer_start_btn = ctk.CTkButton(btn_frame, text="Start Sniffer", fg_color="green", hover_color="darkgreen", command=self.start_sniffer)
        self.sniffer_start_btn.pack(side="left", padx=10)

        self.sniffer_stop_btn = ctk.CTkButton(btn_frame, text="Stop Sniffer", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_sniffer)
        self.sniffer_stop_btn.pack(side="left", padx=10)

    def start_sniffer(self):
        interface = self.sniffer_interface_dropdown.get()
        if not interface:
            self.log("Error: Interface is required for the sniffer.")
            return

        self.sniffer_stop_event.clear()
        self.sniffer_start_btn.configure(state="disabled")
        self.sniffer_stop_btn.configure(state="normal")
        self.log(f"Starting HTTP Sniffer on {interface}...")

        sniffer_instance = Sniffer(interface)
        self.sniffer_thread = threading.Thread(
            target=sniffer_instance.sniff, 
            args=(self.sniffer_stop_event, self.log),
            daemon=True
        )
        self.sniffer_thread.start()

    def stop_sniffer(self):
        self.log("Stopping HTTP Sniffer...")
        self.sniffer_stop_event.set()
        self.sniffer_start_btn.configure(state="normal")
        self.sniffer_stop_btn.configure(state="disabled")

    def destroy(self):
        # Stop all threads before destroying the frame
        self.spoof_stop_event.set()
        self.detector_stop_event.set()
        self.sniffer_stop_event.set()
        super().destroy()
