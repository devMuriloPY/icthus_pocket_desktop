from cryptography.fernet import Fernet
from pathlib import Path
import sys

def get_chave_path():
    """Define um local seguro e gravável para armazenar a chave"""
    if getattr(sys, 'frozen', False):
        # Se empacotado com PyInstaller, salvar no mesmo diretório do .exe
        base_dir = Path(sys.executable).parent
    else:
        # Em modo dev, salvar junto ao projeto
        base_dir = Path(__file__).resolve().parent.parent

    return base_dir / "chave.key"

def gerar_chave():
    chave = Fernet.generate_key()
    chave_path = get_chave_path()
    try:
        with open(chave_path, 'wb') as f:
            f.write(chave)
        return chave
    except Exception as e:
        print(f"❌ Erro ao gerar chave: {e}")
        raise

def carregar_chave():
    chave_path = get_chave_path()
    if not chave_path.exists():
        return gerar_chave()

    try:
        with open(chave_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Erro ao carregar chave: {e}")
        raise

def criptografar_senha(senha: str) -> str:
    chave = carregar_chave()
    f = Fernet(chave)
    return f.encrypt(senha.encode()).decode()

def descriptografar_senha(senha_criptografada: str) -> str:
    chave = carregar_chave()
    f = Fernet(chave)
    return f.decrypt(senha_criptografada.encode()).decode()
