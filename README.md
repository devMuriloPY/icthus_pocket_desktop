# 🖥️ icthus_pocket_desktop

Este é o aplicativo **desktop** do projeto **Icthus Pocket**, desenvolvido em **Python**. Ele funciona como um servidor local que se conecta a um banco de dados SQL Server e expõe uma interface **WebSocket** para que o aplicativo **mobile (Flutter)** possa consultar os produtos disponíveis.

---

## 📡 Visão geral

Quando iniciado, o app:
- Conecta-se ao banco de dados.
- Sobe um servidor WebSocket local.
- Escuta comandos do aplicativo mobile, como `get_produtos`.
- Responde com dados em JSON diretamente do banco.

---

## 🔌 WebSocket API

- **Host padrão:** `0.0.0.0` (aceita conexões de qualquer IP na rede local)
- **Porta padrão:** `5757` (configurável via `config.json`)
- **Formato:** JSON

### ✅ Comando aceito

| Comando        | Descrição                                  |
|----------------|----------------------------------------------|
| `get_produtos` | Retorna lista de produtos ativos no estoque |

### 📤 Exemplo de resposta

```json
{
  "produtos": [
    {
      "Código Item": 101,
      "Descrição Item": "Caneta Azul",
      "Preço Unitário": 3.50,
      "Código Barras": "7891234567890",
      "Estoque Previsto": 120.0
    },
    ...
  ]
}
