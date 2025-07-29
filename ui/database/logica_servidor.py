from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Signal
from ui.database.ui_servidor import Ui_Server

from utils.criptografia import criptografar_senha, descriptografar_senha
from utils.sqlserver import listar_bancos
from utils.imagem import carregar_icon
from utils.rede import obter_ip_local
from utils.config import criar_settings


class TelaServidor(QWidget):
    configuracao_salva = Signal(dict)  # sinal que pode ser conectado ao menu

    def __init__(self):
        super().__init__()
        self.ui = Ui_Server()
        self.ui.setupUi(self)

        self.settings = criar_settings()

        self._configurar_interface()
        self.carregar_configuracoes()

        # Conecta os botões
        self.ui.btnSave.clicked.connect(self.salvar_configuracoes)
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnLoadDatabases.clicked.connect(self.carregar_bancos_disponiveis)

    def _configurar_interface(self):
        self.setWindowIcon(carregar_icon("database.png"))
        self.ui.btnLoadDatabases.setIcon(carregar_icon("reload.png"))
        self.ui.lineEdit_2.setText(obter_ip_local())
        self.ui.lineEdit_2.setReadOnly(True)

    def carregar_configuracoes(self):
        self.ui.leServer.setText(self.settings.value("servidor", "localhost"))
        self.ui.leUser.setText(self.settings.value("usuario", "sa"))

        senha_cripto = self.settings.value("senha", "")
        try:
            senha = descriptografar_senha(senha_cripto) if senha_cripto else ""
        except Exception:
            senha = ""
        self.ui.lePassword.setText(senha)

        self.ui.lineEdit.setText(self.settings.value("porta", "5757"))

        banco_salvo = self.settings.value("banco", "")
        if banco_salvo:
            self.ui.cbDatabase.addItem(banco_salvo)

    def salvar_configuracoes(self):
        servidor = self.ui.leServer.text().strip()
        usuario = self.ui.leUser.text().strip()
        senha = self.ui.lePassword.text().strip()
        porta = self.ui.lineEdit.text().strip()
        ip = self.ui.lineEdit_2.text().strip()
        banco = self.ui.cbDatabase.currentText().strip()

        senha_cripto = criptografar_senha(senha) if senha else ""

        self.settings.setValue("servidor", servidor)
        self.settings.setValue("usuario", usuario)
        self.settings.setValue("senha", senha_cripto)
        self.settings.setValue("porta", porta)
        self.settings.setValue("ip", ip)
        self.settings.setValue("banco", banco)

        self.configuracao_salva.emit({
            "servidor": servidor,
            "usuario": usuario,
            "senha": senha,
            "banco": banco,
            "ip": ip,
            "porta": porta
        })

        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        self.close()

    def carregar_bancos_disponiveis(self):
        servidor = self.ui.leServer.text().strip()
        usuario = self.ui.leUser.text().strip()
        senha = self.ui.lePassword.text().strip()

        if not servidor or not usuario or not senha:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha servidor, usuário e senha antes.")
            return

        bancos = listar_bancos(servidor, usuario, senha)

        self.ui.cbDatabase.clear()

        if isinstance(bancos, list):
            self.ui.cbDatabase.addItems(bancos)
        else:
            QMessageBox.critical(self, "Erro ao listar bancos", bancos)
