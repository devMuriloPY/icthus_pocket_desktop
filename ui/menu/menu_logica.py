from PySide6.QtWidgets import QMainWindow, QApplication
import sys

from ui.menu.ui_menu import Ui_Menu
from ui.database.logica_servidor import TelaServidor
from utils.imagem import carregar_icon

class MenuPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Menu()
        self.ui.setupUi(self)

        # Conecta ações do menu
        self.setWindowIcon(carregar_icon("logo.png"))
        self.ui.actionDatabase.triggered.connect(self.abrir_configuracao_banco)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionDatabase.setIcon(carregar_icon("database.png"))
        self.ui.actionExit.setIcon(carregar_icon("exit.png"))

    def abrir_configuracao_banco(self):
        self.tela_config = TelaServidor()
        self.tela_config.configuracao_salva.connect(self.configuracao_recebida)
        self.tela_config.show()

    def configuracao_recebida(self, config: dict):
        print("⚙️ Configuração recebida do banco:")
        for chave, valor in config.items():
            print(f"  {chave}: {valor}")
        # Aqui você pode usar os dados como quiser
