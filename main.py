import sys
import os
import msvcrt
import atexit

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer

from ui.menu.menu_logica import MenuPrincipal
from utils.imagem import carregar_icon
from utils.websocket_server import iniciar_websocket_em_thread
from utils.config import criar_settings
from utils.usuarios_windows import obter_usuario_atual

# Caminho para o arquivo de lock por usuário
# Usa %LOCALAPPDATA% que sempre tem permissão de escrita e é específico por usuário
# Permite múltiplos usuários no servidor, cada um com sua própria instância
def obter_caminho_lock():
    """Retorna o caminho do arquivo de lock para o usuário atual."""
    local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    lock_dir = os.path.join(local_appdata, "ICThUS Pocket")
    os.makedirs(lock_dir, exist_ok=True)  # Garante que o diretório existe
    username = os.environ.get("USERNAME", "unknown")
    return os.path.join(lock_dir, f"icthus-pocket-{username}.lock")

LOCK_FILE_PATH = obter_caminho_lock()
LOCK_FILE = None


def checar_instancia_usuario():
    """Impede múltiplas instâncias do app para o mesmo usuário."""
    global LOCK_FILE, LOCK_FILE_PATH
    try:
        # Atualiza o caminho caso tenha mudado
        LOCK_FILE_PATH = obter_caminho_lock()
        
        # Tenta abrir e travar o arquivo
        LOCK_FILE = open(LOCK_FILE_PATH, "w")
        msvcrt.locking(LOCK_FILE.fileno(), msvcrt.LK_NBLCK, 1)
        
        # Escreve informações sobre a instância em execução
        LOCK_FILE.write(f"PID: {os.getpid()}\nUsuário: {os.environ.get('USERNAME', 'Desconhecido')}\n")
        LOCK_FILE.flush()
        
        return True
    except (OSError, IOError, PermissionError) as e:
        # Arquivo já está travado por outra instância do mesmo usuário
        print(f"Aviso: Não foi possível criar lock: {e}")
        return False


def liberar_lock():
    """Libera o arquivo de lock ao encerrar o app."""
    global LOCK_FILE
    if LOCK_FILE:
        try:
            msvcrt.locking(LOCK_FILE.fileno(), msvcrt.LK_UNLCK, 1)
            LOCK_FILE.close()
            # Remove o arquivo de lock
            if os.path.exists(LOCK_FILE_PATH):
                os.remove(LOCK_FILE_PATH)
        except Exception as e:
            print(f"Aviso ao liberar lock: {e}")


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


def verificar_usuario_permitido():
    """Verifica se o usuário atual do Windows está autorizado a iniciar o app."""
    try:
        settings = criar_settings()
        usuario_configurado = settings.value("usuario_windows", "")
        
        # Se não houver usuário configurado, permite qualquer usuário (comportamento antigo)
        if not usuario_configurado or usuario_configurado.strip() == "":
            return True
        
        usuario_atual = obter_usuario_atual()
        
        # Verifica se o usuário atual corresponde ao configurado
        if usuario_atual.lower() == usuario_configurado.lower():
            return True
        
        # Usuário não autorizado
        return False
    except Exception as e:
        print(f"⚠️ Erro ao verificar usuário permitido: {e}")
        # Em caso de erro, permite o acesso (comportamento seguro)
        return True


def main():
    # Verifica se o usuário atual está autorizado a iniciar o app
    if not verificar_usuario_permitido():
        app_temp = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        usuario_atual = obter_usuario_atual()
        settings = criar_settings()
        usuario_configurado = settings.value("usuario_windows", "")
        
        QMessageBox.warning(
            None, 
            "Acesso Negado", 
            f"O ICThUS Pocket Sync está configurado para iniciar apenas com o usuário '{usuario_configurado}'.\n\n"
            f"Usuário atual: '{usuario_atual}'\n\n"
            "Para alterar esta configuração, acesse as Configurações do aplicativo."
        )
        sys.exit(0)
    
    if not checar_instancia_usuario():
        app_temp = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        username = os.environ.get("USERNAME", "usuário")
        QMessageBox.warning(
            None, 
            "Aplicativo já em execução", 
            f"O ICThUS Pocket Sync já está rodando para o usuário '{username}'.\n\n"
            "Apenas uma instância do aplicativo pode ser executada por usuário.\n"
            "Cada usuário no servidor pode ter sua própria instância."
        )
        sys.exit(0)
    
    # Registra a liberação do lock ao sair do programa (mesmo em crashes)
    atexit.register(liberar_lock)

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

    # Inicia o WebSocket diretamente no app desktop
    iniciar_websocket_em_thread()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
