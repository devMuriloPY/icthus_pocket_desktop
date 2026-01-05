from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Signal
from ui.database.ui_servidor import Ui_Server

from utils.criptografia import criptografar_senha, descriptografar_senha
from utils.sqlserver import listar_bancos
from utils.imagem import carregar_icon
from utils.rede import obter_ip_local
from utils.config import criar_settings
from utils.impressora import listar_impressoras_windows
from utils.usuarios_windows import listar_usuarios_windows, obter_usuario_atual


class TelaServidor(QWidget):
    configuracao_salva = Signal(dict)  # sinal que pode ser conectado ao menu

    def __init__(self):
        super().__init__()
        self.ui = Ui_Server()
        self.ui.setupUi(self)

        self.settings = criar_settings()

        self._configurar_interface()
        self.carregar_impressoras()
        self.carregar_usuarios_windows()
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

    def carregar_impressoras(self):
        """Carrega as impressoras disponíveis no Windows no combobox."""
        try:
            impressoras = listar_impressoras_windows()
            self.ui.cbImpressora.clear()
            
            if impressoras:
                self.ui.cbImpressora.addItems(impressoras)
            else:
                self.ui.cbImpressora.addItem("Nenhuma impressora encontrada")
        except Exception as e:
            print(f"⚠️ Erro ao carregar impressoras: {e}")
            self.ui.cbImpressora.addItem("Erro ao carregar impressoras")

    def carregar_usuarios_windows(self):
        """Carrega os usuários do Windows disponíveis no combobox."""
        try:
            usuarios = listar_usuarios_windows()
            self.ui.cbUsuarioWindows.clear()
            
            if usuarios:
                self.ui.cbUsuarioWindows.addItems(usuarios)
            else:
                # Se não encontrar usuários, adiciona pelo menos o atual
                usuario_atual = obter_usuario_atual()
                self.ui.cbUsuarioWindows.addItem(usuario_atual)
        except Exception as e:
            print(f"⚠️ Erro ao carregar usuários do Windows: {e}")
            usuario_atual = obter_usuario_atual()
            self.ui.cbUsuarioWindows.addItem(usuario_atual)

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
        
        # Carrega a impressora salva
        impressora_salva = self.settings.value("impressora", "")
        if impressora_salva:
            index = self.ui.cbImpressora.findText(impressora_salva)
            if index >= 0:
                self.ui.cbImpressora.setCurrentIndex(index)
        
        # Carrega colunas da impressora (padrão: 42 para papel 80mm)
        colunas = self.settings.value("colunas_impressora", "42")
        self.ui.leColunas.setText(str(colunas))
        
        # Carrega o usuário do Windows configurado para inicialização automática
        usuario_windows = self.settings.value("usuario_windows", "")
        if usuario_windows:
            index = self.ui.cbUsuarioWindows.findText(usuario_windows)
            if index >= 0:
                self.ui.cbUsuarioWindows.setCurrentIndex(index)
            else:
                # Se o usuário salvo não estiver na lista, adiciona
                self.ui.cbUsuarioWindows.addItem(usuario_windows)
                self.ui.cbUsuarioWindows.setCurrentText(usuario_windows)
        else:
            # Se não houver usuário configurado, seleciona o usuário atual
            usuario_atual = obter_usuario_atual()
            index = self.ui.cbUsuarioWindows.findText(usuario_atual)
            if index >= 0:
                self.ui.cbUsuarioWindows.setCurrentIndex(index)

    def salvar_configuracoes(self):
        servidor = self.ui.leServer.text().strip()
        usuario = self.ui.leUser.text().strip()
        senha = self.ui.lePassword.text().strip()
        porta = self.ui.lineEdit.text().strip()
        ip = self.ui.lineEdit_2.text().strip()
        banco = self.ui.cbDatabase.currentText().strip()
        impressora = self.ui.cbImpressora.currentText().strip()
        colunas = self.ui.leColunas.text().strip()
        usuario_windows = self.ui.cbUsuarioWindows.currentText().strip()

        # Valida colunas (deve ser número entre 20 e 80)
        try:
            colunas_int = int(colunas) if colunas else 42
            if colunas_int < 20 or colunas_int > 80:
                QMessageBox.warning(self, "Valor inválido", "O número de colunas deve estar entre 20 e 80.")
                return
            colunas = str(colunas_int)
        except ValueError:
            QMessageBox.warning(self, "Valor inválido", "O número de colunas deve ser um número inteiro.")
            return

        senha_cripto = criptografar_senha(senha) if senha else ""

        self.settings.setValue("servidor", servidor)
        self.settings.setValue("usuario", usuario)
        self.settings.setValue("senha", senha_cripto)
        self.settings.setValue("porta", porta)
        self.settings.setValue("ip", ip)
        self.settings.setValue("banco", banco)
        self.settings.setValue("impressora", impressora)
        self.settings.setValue("colunas_impressora", colunas)
        self.settings.setValue("usuario_windows", usuario_windows)

        self.configuracao_salva.emit({
            "servidor": servidor,
            "usuario": usuario,
            "senha": senha,
            "banco": banco,
            "ip": ip,
            "porta": porta,
            "impressora": impressora,
            "colunas_impressora": colunas,
            "usuario_windows": usuario_windows
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
