import asyncio
import websockets
import json
import threading

from utils.sqlserver import conexao_ativa
from utils.config import criar_settings  # ✅ Config JSON

def obter_porta_websocket(padrao=5757):
    """Lê a porta configurada no config.json, ou usa a padrão."""
    settings = criar_settings()
    porta_str = settings.value("porta", str(padrao))
    try:
        return int(porta_str)
    except (ValueError, TypeError):
        return padrao

async def processar_conexao(websocket):
    """Processa os comandos recebidos via WebSocket."""
    try:
        async for mensagem in websocket:
            if mensagem == "get_produtos":
                await enviar_lista_produtos(websocket)
            else:
                await websocket.send(json.dumps({"erro": "comando inválido"}))
    except websockets.ConnectionClosedError as e:
        print(f"⚠️ Conexão fechada inesperadamente: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado no WebSocket: {e}")
    finally:
        print("🔒 Conexão WebSocket encerrada")

async def enviar_lista_produtos(websocket):
    """Executa a consulta no banco e envia os produtos."""
    try:
        print("📡 Recebido comando get_produtos via WebSocket")
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT [Código Item], [Descrição Item], [Preço Unitário], [Código Barras], [Estoque Previsto]
            FROM Estoque WHERE Ativo = 1
        """)
        produtos = [
            {
                "Código Item": row[0],
                "Descrição Item": row[1],
                "Preço Unitário": float(row[2]),
                "Código Barras": row[3],
                "Estoque Previsto": float(row[4])
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        await websocket.send(json.dumps({"produtos": produtos}))
    except Exception as e:
        await websocket.send(json.dumps({"erro": str(e)}))

async def iniciar_servidor(porta):
    """Inicia o servidor WebSocket assíncrono."""
    try:
        print(f"🔌 WebSocket escutando na porta {porta}")
        async with websockets.serve(
            processar_conexao,
            "0.0.0.0",
            porta,
            ping_interval=30,
            ping_timeout=10
        ):
            await asyncio.Future()  # Aguarda indefinidamente
    except Exception as e:
        print(f"❌ Falha ao iniciar WebSocket: {e}")

def iniciar_websocket_em_thread(porta=None):
    """Inicia o WebSocket em uma thread separada (modo daemon)."""
    if porta is None:
        porta = obter_porta_websocket()
    t = threading.Thread(target=lambda: asyncio.run(iniciar_servidor(porta)))
    t.daemon = True
    t.start()
