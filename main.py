"""
F1 Manager 2026 — main.py
Janela desktop PyQt6 com interface HTML/CSS + WebSocket para corridas.
"""

import sys
import os
import subprocess
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSlot, QObject
from PyQt6.QtWebChannel import QWebChannel

BASE = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE, "ui", "index.html")
RACE_PATH = os.path.join(BASE, "ui", "race.html")

server_proc = None

def start_race_server():
    global server_proc
    if server_proc and server_proc.poll() is None:
        return  # já está a correr
    server_proc = subprocess.Popen(
        [sys.executable, os.path.join(BASE, "race_server.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[Server] Iniciado PID {server_proc.pid}")

def stop_race_server():
    global server_proc
    if server_proc and server_proc.poll() is None:
        server_proc.terminate()
        print("[Server] Terminado")


class F1ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Manager 2026")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)

        self.browser = QWebEngineView()
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        self.browser.load(QUrl.fromLocalFile(UI_PATH))
        self.setCentralWidget(self.browser)

        # Intercept navigation to race.html
        self.browser.urlChanged.connect(self._on_url_changed)

    def _on_url_changed(self, url):
        path = url.toLocalFile()
        if path and "race.html" in path:
            start_race_server()

    def closeEvent(self, event):
        stop_race_server()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("F1 Manager 2026")
    window = F1ManagerWindow()
    window.show()
    sys.exit(app.exec())
