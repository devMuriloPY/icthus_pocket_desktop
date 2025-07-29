import pyodbc
from utils.config import criar_settings
from utils.criptografia import descriptografar_senha


def listar_bancos(servidor, usuario, senha):
    """Lista os bancos disponíveis em um servidor SQL Server."""
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={servidor};UID={usuario};PWD={senha}'
        )
        conexao = pyodbc.connect(conn_str, timeout=3)
        cursor = conexao.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
        bancos = [row[0] for row in cursor.fetchall()]
        conexao.close()
        return bancos

    except Exception as e:
        return f"Erro: {str(e)}"


def conexao_ativa():
    """Retorna uma conexão ativa com o banco de dados usando os dados do config.json."""
    settings = criar_settings()

    servidor = settings.value("servidor", "localhost")
    usuario = settings.value("usuario", "sa")
    senha_cripto = settings.value("senha", "")
    banco = settings.value("banco", "")

    try:
        senha = descriptografar_senha(senha_cripto) if senha_cripto else ""
    except Exception:
        senha = ""

    if not banco:
        raise Exception("Nenhum banco de dados foi selecionado.")

    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={servidor};DATABASE={banco};UID={usuario};PWD={senha}'
        )
        conexao = pyodbc.connect(conn_str, timeout=5)
        return conexao

    except Exception as e:
        raise Exception(f"Erro ao conectar no banco: {str(e)}")
