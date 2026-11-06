"""
F1 Manager 2026 — launch.py
Arranca o servidor de corrida e o jogo em simultâneo.
"""

import subprocess
import sys
import os
import time
import signal

BASE = os.path.dirname(os.path.abspath(__file__))

def main():
    print("[F1 Manager] A iniciar...")

    # Arrancar servidor WebSocket em background
    server = subprocess.Popen(
        [sys.executable, os.path.join(BASE, "race_server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"[F1 Manager] Servidor de corrida iniciado (PID {server.pid})")
    time.sleep(1.5)  # esperar o servidor arrancar

    # Arrancar o jogo principal
    try:
        game = subprocess.Popen(
            [sys.executable, os.path.join(BASE, "main.py")],
        )
        print(f"[F1 Manager] Jogo iniciado (PID {game.pid})")
        game.wait()
    finally:
        print("[F1 Manager] A fechar servidor...")
        server.terminate()
        try:
            server.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()
        print("[F1 Manager] Fechado.")

if __name__ == "__main__":
    main()
