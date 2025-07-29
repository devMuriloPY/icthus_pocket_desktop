import sys
import os
import msvcrt
import tempfile

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer

from ui.menu.menu_logica import MenuPrincipal
from utils.websocket_server import iniciar_websocket_em_thread
from utils.imagem import carregar_icon
from utils.config import criar_settings  # ✅ Novo sistema de configuração

# Caminho para o arquivo de lock global
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), "icthus-pocket-global.lock")
LOCK_FILE = None


def checar_instancia_global():
    """Impede múltiplas instâncias do app na mesma máquina (mesmo entre usuários)."""
    global LOCK_FILE
    try:
        LOCK_FILE = open(LOCK_FILE_PATH, "w")
        msvcrt.locking(LOCK_FILE.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False


def liberar_lock():
    """Libera o arquivo de lock ao encerrar o app."""
    global LOCK_FILE
    if LOCK_FILE:
        try:
            msvcrt.locking(LOCK_FILE.fileno(), msvcrt.LK_UNLCK, 1)
            LOCK_FILE.close()
        except:
            pass


class AppTray:
    """Gerencia o ícone da bandeja e seu menu de contexto."""

    def __init__(self, janela: MenuPrincipal, app: QApplication):
        self.janela = janela
        self.app = app
        self.tray = QSystemTrayIcon(carregar_icon("logo.png"), app)

        self.menu = QMenu()
        self.acao_restaurar = QAction("Restaurar")
        self.acao_sair = QAction("Sair")

        self.acao_restaurar.triggered.connect(self.mostrar_janela)
        self.acao_sair.triggered.connect(self.sair_app)

        self.menu.addAction(self.acao_restaurar)
        self.menu.addSeparator()
        self.menu.addAction(self.acao_sair)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("ICThUS Pocket - rodando em segundo plano")
        self.tray.activated.connect(self.icone_clicado)
        self.tray.show()

    def mostrar_janela(self):
        self.janela.showNormal()
        self.janela.activateWindow()

    def icone_clicado(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.mostrar_janela()

    def sair_app(self):
        self.tray.hide()
        self.app.quit()


def main():
    if not checar_instancia_global():
        QMessageBox.warning(None, "Já em execução", "O aplicativo já está rodando.")
        sys.exit(0)

    app = QApplication(sys.argv)
    janela = MenuPrincipal()
    tray = AppTray(janela, app)

    encerrando = {"valor": False}

    def ao_fechar(event):
        if encerrando["valor"]:
            event.accept()
        else:
            event.ignore()
            janela.hide()
            QTimer.singleShot(100, lambda: tray.tray.showMessage(
                "ICThUS Pocket",
                "O sistema foi minimizado para a bandeja.",
                QSystemTrayIcon.Information,
                3000
            ))

    janela.closeEvent = ao_fechar

    def sair_completo():
        encerrando["valor"] = True
        tray.tray.hide()
        janela.close()
        liberar_lock()
        app.quit()

    janela.ui.actionExit.triggered.connect(sair_completo)

    janela.show()

    # ✅ Iniciar WebSocket com a porta definida no config.json
    settings = criar_settings()
    porta_configurada = settings.value("porta", 5757)
    try:
        porta_configurada = int(porta_configurada)
    except (ValueError, TypeError):
        porta_configurada = 5757

    iniciar_websocket_em_thread(porta_configurada)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
