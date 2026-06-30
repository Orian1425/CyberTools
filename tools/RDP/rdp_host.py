import os, queue, socket, threading, time, cv2, numpy as np, struct
from tools.RDP.listeners import MouseListener, KeyboardListener

class Host: # Protocol - k:a - keyboard, M:10,10 - mouse coords, B:mouse buttons
    def __init__(self, addr: str, port: int, shutdown_callback=None, log_callback=None):
        self.addr = addr
        self.port = port
        self.shutdown_callback = shutdown_callback
        self.log = log_callback or print
        
        self.kb_mouse_socket = None
        self.video_socket = None
        self.kb_mouse_con = None

        self.q = None
        self.mouse_listener = None
        self.kb_listener = None

        self.last_frame = None
        self.is_running = False
        self.kb_mouse_thread = None
        self.video_thread = None

    def start(self):
        self.is_running = True
        self.kb_mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.kb_mouse_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.kb_mouse_socket.bind((self.addr, self.port))
        self.kb_mouse_socket.listen()
        
        # Accept connection without blocking indefinitely so we can stop if needed
        self.kb_mouse_socket.settimeout(1.0)
        while self.is_running:
            try:
                self.kb_mouse_con, self.client_addr = self.kb_mouse_socket.accept()
                break
            except socket.timeout:
                continue
            except Exception:
                return False

        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket.bind((self.addr, self.port))

        if not self.is_running:
            return False

        self.q = queue.Queue()

        self.mouse_listener = MouseListener(self.q)
        self.kb_listener = KeyboardListener(self.q, self.shutdown_callback)

        self.start_input_capture()
        self.kb_mouse_thread = threading.Thread(target=self.handling_KB_and_mouse_data, args=(self.kb_mouse_con,), daemon=True)
        self.kb_mouse_thread.start()

        # Start the network listener in the background
        self.video_thread = threading.Thread(target=self.network_video_packet_listener, daemon=True)
        self.video_thread.start()
        
        # Start the GUI loop
        self.gui_loop()
        return True
     
    def start_input_capture(self):
        self.mouse_listener.start_listening()
        self.kb_listener.start_listening()

    def handling_KB_and_mouse_data(self, con: socket.socket):
        while self.is_running:
            try:
                try:
                    data = self.q.get(timeout=1.0)
                except queue.Empty:
                    continue
                con.sendall(f"{data}\n".encode())
                self.q.task_done()
            except Exception as e:
                self.log(f"Connection lost: {e}")
                self.stop()
                break

    def gui_loop(self):
        """Runs on the RDP thread. Only handles displaying the video."""
        cv2.namedWindow('Screen Recording', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Screen Recording', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while self.is_running:
            # If the background thread has provided a frame, show it
            if self.last_frame is not None:
                cv2.imshow('Screen Recording', self.last_frame)
            
            if cv2.waitKey(1) == ord('q') and self.kb_listener.is_ctrl_pressed():
                self.stop()
                break
        cv2.destroyAllWindows()
    

    def network_video_packet_listener(self):
        frame_buffer = {}
        self.video_socket.settimeout(1.0)
        while self.is_running:
            try:
                packet, addr = self.video_socket.recvfrom(65535)
            except socket.timeout:
                continue
            except Exception:
                self.stop()
                break

            header = packet[:6]
            chunk_data = packet[6:]

            frame_id, chunk_id, total_chunks = struct.unpack('I B B', header)
            if frame_id not in frame_buffer:
                frame_buffer[frame_id] = [None] * total_chunks # initialize item in list for every chunk
            frame_buffer[frame_id][chunk_id] = chunk_data

            if None not in frame_buffer[frame_id]: # all chunks have the data
                full_frame_data = b''.join(frame_buffer[frame_id])

                np_arr = np.frombuffer(full_frame_data, dtype=np.uint8) # convert bytes to np array
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # decode np array to jpg

                if frame is not None:
                    self.last_frame = frame

                del frame_buffer[frame_id]

    def stop(self):
        self.is_running = False
        
        # Stop pynput listeners
        if self.mouse_listener:
            try:
                self.mouse_listener.listener.stop()
            except Exception:
                pass
        if self.kb_listener:
            try:
                self.kb_listener.listener.stop()
            except Exception:
                pass

        # Close sockets
        if self.kb_mouse_con:
            try:
                self.kb_mouse_con.close()
            except Exception:
                pass
        if self.kb_mouse_socket:
            try:
                self.kb_mouse_socket.close()
            except Exception:
                pass
        if self.video_socket:
            try:
                self.video_socket.close()
            except Exception:
                pass

        # Destroy CV2 windows
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    @staticmethod
    def broadcast_presence(stop_event: threading.Event, broadcast_port: int = 50001, log_callback=None):
        if log_callback is None:
            log_callback = print
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Unique token so your client knows it's actually your server
        magic_token = b"Orian" 
        
        try:
            while not stop_event.is_set():
                # Broadcast the token to everyone on the local subnet
                sock.sendto(magic_token, ('<broadcast>', broadcast_port))
                # Sleep in short intervals so we can exit quickly
                for _ in range(30):
                    if stop_event.is_set():
                        break
                    time.sleep(0.1)
        except Exception as e:
            log_callback(f"Stopping broadcast due to: {e}")
        finally:
            sock.close()


            


# if __name__ == "__main__":
#     try:
#         import config
#         rdp_port = config.PORTS.get("RDP", 7777)
#         broadcast_port = config.PORTS.get("Broadcast", 50001)
#     except ImportError:
#         rdp_port = 7777
#         broadcast_port = 50001

#     stop_event = threading.Event()
#     t = threading.Thread(target=broadcast_presence, args=(stop_event, broadcast_port), daemon=True)
#     t.start()
    
#     host = Host("0.0.0.0", rdp_port)
#     try:
#         host.start()
#     except KeyboardInterrupt:
#         print("Stopping host...")
#     finally:
#         stop_event.set()
#         host.stop()