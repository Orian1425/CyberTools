import os
import requests
import time
import threading

class VirusTotalScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }

    def scan_file(self, file_path, callback, done_event: threading.Event = None):
        """
        מריץ את הסריקה ב-Thread נפרד כדי לא לתקוע את ה-GUI.
        בסיום, קורא לפונקציית callback עם התוצאה.
        """
        def task():
            if os.path.getsize(file_path) == 0:
                callback(f"Skipping empty file: {os.path.basename(file_path)}")
                return

            try:
                # 1. העלאת הקובץ
                url = "https://www.virustotal.com/api/v3/files"
                with open(file_path, 'rb') as f:
                    files = {"file": (os.path.basename(file_path), f)}
                    response = requests.post(url, files=files, headers=self.headers)
                
                if response.status_code != 200:
                    callback(f"Error: {response.json().get('error', {}).get('message')}")
                    return

                analysis_id = response.json()["data"]["id"]
                
                # 2. המתנה לתוצאות
                analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                while True:
                    analysis = requests.get(analysis_url, headers=self.headers)
                    data = analysis.json()["data"]["attributes"]
                    if data["status"] == "completed":
                        # שליפת תוצאה כללית (כמות מנועים שזיהו כזדוני)
                        stats = data["stats"]
                        res_msg = f"Malicious: {stats['malicious']}, Undetected: {stats['undetected']}"
                        callback(f"File: {os.path.basename(file_path)} | {res_msg}")
                        break
                    time.sleep(2)

            except Exception as e:
                callback(f"Exception: {str(e)}")
            finally:
                if done_event:
                    done_event.set()

        threading.Thread(target=task, daemon=True).start()