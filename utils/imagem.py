from PySide6.QtGui import QIcon, QPixmap
import os

def caminho_imagem(nome_arquivo: str) -> str:
    """
    Retorna o caminho absoluto da imagem na pasta assets/images/.
    Se não encontrar, retorna caminho da imagem padrão (default.png).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.normpath(os.path.join(base_dir, "..", "assets", "images", nome_arquivo))

    if not os.path.exists(caminho):
        print(f"⚠️ Imagem '{nome_arquivo}' não encontrada. Usando 'default.png'.")
        caminho_default = os.path.normpath(os.path.join(base_dir, "..", "assets", "images", "default.png"))
        return caminho_default if os.path.exists(caminho_default) else ""
    
    return caminho

def carregar_icon(nome_arquivo: str) -> QIcon:
    """
    Retorna um QIcon da imagem solicitada. Usa fallback se imagem não for encontrada.
    """
    caminho = caminho_imagem(nome_arquivo)
    if caminho:
        return QIcon(caminho)
    return QIcon()

def carregar_pixmap(nome_arquivo: str) -> QPixmap:
    """
    Retorna um QPixmap da imagem solicitada. Usa fallback se imagem não for encontrada.
    """
    caminho = caminho_imagem(nome_arquivo)
    if caminho:
        return QPixmap(caminho)
    return QPixmap()
