"""
Ponto de entrada para a versão desktop (Windows), empacotada com PyInstaller.

Sobe o app Dash definido em main.py num servidor Flask local e abre uma
janela nativa (pywebview) apontando para ele, sem depender do usuário ter
Python instalado. Para desenvolvimento no terminal/Codespace, use main.py
diretamente.
"""

import threading

import webview

from main import app


def rodar_servidor():
    app.run(debug=False, port=8050, use_reloader=False)


if __name__ == "__main__":
    threading.Thread(target=rodar_servidor, daemon=True).start()
    webview.create_window(
        "Dashboard DMAE",
        "http://127.0.0.1:8050",
        width=1400,
        height=900,
    )
    webview.start()
