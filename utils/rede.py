import socket

def obter_ip_local() -> str:
    """
    Retorna o IP local IPv4 da máquina.
    Se falhar, retorna 127.0.0.1 como fallback.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "127.0.0.1"
