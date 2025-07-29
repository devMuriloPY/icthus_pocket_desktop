import json
import sys
from pathlib import Path

def obter_caminho_config():
    """Define onde o config.json será salvo:
    - No mesmo diretório do .exe (modo empacotado)
    - No mesmo nível do main.py (modo desenvolvimento)
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / 'config.json'
    else:
        return Path(__file__).resolve().parent.parent / 'config.json'


CONFIG_PATH = obter_caminho_config()


def criar_settings():
    """Inicializa e retorna um manipulador de configurações."""
    return Configuracoes()


class Configuracoes:
    def __init__(self):
        self.config_file = CONFIG_PATH
        self._dados = self._carregar()

    def _carregar(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ config.json corrompido. Usando valores padrão.")
                return self._criar_padrao()
        else:
            return self._criar_padrao()

    def _criar_padrao(self):
        """Cria o dicionário padrão e salva"""
        self._dados = {
            "porta": "5757",
            "servidor": "localhost",
            "usuario": "sa",
            "senha": "",
            "banco": ""
        }
        self._salvar()
        return self._dados

    def _salvar(self):
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar config.json: {e}")

    def value(self, chave, padrao=None):
        """Lê um valor da configuração"""
        return self._dados.get(chave, padrao)

    def setValue(self, chave, valor):
        """Salva um valor na configuração"""
        self._dados[chave] = valor
        self._salvar()
