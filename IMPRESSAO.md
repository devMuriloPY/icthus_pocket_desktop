# 🖨️ Sistema de Impressão - ICThUS Pocket Sync

Sistema de impressão térmica para impressoras de 80mm integrado ao ICThUS Pocket Sync.

## 📋 Requisitos

- **Biblioteca:** `pywin32==306` (já incluída no `requirements.txt`)
- **Impressora:** Térmica de 80mm (42 colunas)
- **Sistema:** Windows com impressora instalada

## ⚙️ Configuração

### 1. Instalação da Biblioteca

```bash
pip install pywin32==306
```

### 2. Configurar Impressora e Largura do Papel

1. Abra a tela de configuração do servidor (menu principal)
2. No campo **"Impressora"**, selecione a impressora desejada
3. No campo **"Colunas"**, configure a largura do papel:
   - **42 colunas** - Papel 80mm (padrão)
   - **32 colunas** - Papel 58mm (impressoras menores como Epson)
   - Valores permitidos: **20 a 80 colunas**
4. Clique em **"Salvar"**
5. A configuração ficará salva no `config.json`

A impressora e largura configuradas serão usadas para todas as impressões via WebSocket.

### 📏 Guia de Colunas por Tamanho de Papel

| Largura do Papel | Colunas Recomendadas | Impressoras Comuns |
|------------------|---------------------|-------------------|
| 80mm | 42-48 colunas | Padrão (maioria) |
| 58mm | 32-36 colunas | Epson TM-T20, Bematech |
| 44mm | 24-28 colunas | Impressoras portáteis |

**Dica:** Se as linhas estiverem "pulando" para a próxima linha, **diminua** o número de colunas.

## 🔌 Uso via WebSocket

### Comando: `imprimir_venda`

Imprime um cupom de venda de um pedido existente no banco de dados.

#### Requisição

```json
{
  "comando": "imprimir_venda",
  "cod_pedido": "0000000123"
}
```

#### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `comando` | string | Sim | Deve ser `"imprimir_venda"` |
| `cod_pedido` | string | Sim | Código do pedido a ser impresso |

#### Resposta de Sucesso

```json
{
  "sucesso": true,
  "mensagem": "Cupom do pedido 0000000123 impresso com sucesso"
}
```

#### Resposta de Erro

```json
{
  "sucesso": false,
  "erro": "Pedido não encontrado"
}
```

## 📄 Formato do Cupom

O cupom impresso contém:

### Cabeçalho
- Nome da empresa (centralizado, negrito, tamanho grande)
- Título "CUPOM DE VENDA"
- Código do pedido
- Data e hora de emissão

### Dados da Venda
- Nome do cliente
- Endereço completo do cliente (rua, número, bairro, cidade/estado, CEP)
- Nome do vendedor
- Responsável pela venda (se informado)
- Forma de pagamento (do mobile, ou "Não informado" se não enviado)

### Itens
Para cada item:
- Descrição do produto (até 24 caracteres)
- Valor unitário
- Quantidade
- Valor total do item

### Rodapé
- Quantidade total de itens
- Valor total da venda (destacado)
- Mensagem de agradecimento
- Assinatura: "Desenvolvido por WM Sistemas de Gestão"
- Corte parcial do papel

### Exemplo de Cupom

```
          LOJA EXEMPLO LTDA
==========================================
           CUPOM DE VENDA
==========================================

Pedido: 0000000123
Data: 05/11/2025 14:30:25

Cliente: JOAO DA SILVA
RUA DAS FLORES, N 123
CENTRO - SAO PAULO/SP - CEP: 01234-567

Vendedor: MARIA SANTOS
Resp.: CARLOS SOUZA
Pgto: Dinheiro

------------------------------------------
ITEM                      QTD  TOTAL
------------------------------------------
PRODUTO TESTE 1
 R$ 10.00 x2.00               R$ 20.00

PRODUTO TESTE 2
 R$ 15.50 x1.00               R$ 15.50

------------------------------------------
Qtd. Total: 3.00
==========================================
TOTAL:                        R$ 35.50
==========================================

     Obrigado pela preferencia!


       Desenvolvido por
     WM Sistemas de Gestao


[Corte Parcial]
```

### Exemplo de Orçamento (DocumentoVenda = 2)

```
          LOJA EXEMPLO LTDA
==========================================
         CUPOM DE ORCAMENTO
==========================================

Orcamento: 0000000124
Data: 05/11/2025 15:00:00

Cliente: MARIA SANTOS
AV PAULISTA, N 1000
BELA VISTA - SAO PAULO/SP

Vendedor: JOSE SILVA
Pgto: A Vista

------------------------------------------
ITEM                      QTD  TOTAL
------------------------------------------
PRODUTO A
 R$ 25.00 x2.00               R$ 50.00

------------------------------------------
Qtd. Total: 2.00
==========================================
TOTAL:                        R$ 50.00
==========================================

     Obrigado pela preferencia!


       Desenvolvido por
     WM Sistemas de Gestao


[Corte Parcial]
```

### Exemplo de Condicional (DocumentoVenda = 3)

```
          LOJA EXEMPLO LTDA
==========================================
         CUPOM CONDICIONAL
==========================================

Condicional: 0000000125
Data: 05/11/2025 16:30:00

Cliente: PEDRO OLIVEIRA
RUA DO COMERCIO, N 50
COMERCIAL - SAO PAULO/SP

Vendedor: ANA COSTA
Pgto: Nao informado

------------------------------------------
ITEM                      QTD  TOTAL
------------------------------------------
PRODUTO B
 R$ 100.00 x1.00             R$ 100.00

------------------------------------------
Qtd. Total: 1.00
==========================================
TOTAL:                       R$ 100.00
==========================================

     Obrigado pela preferencia!


       Desenvolvido por
     WM Sistemas de Gestao


[Corte Parcial]
```

## 🔧 Funções Disponíveis (Python)

### `listar_impressoras_windows()`
Lista todas as impressoras instaladas no Windows.

```python
from utils.impressora import listar_impressoras_windows

impressoras = listar_impressoras_windows()
print(impressoras)
# ['Microsoft Print to PDF', 'EPSON TM-T20', ...]
```

### `obter_impressora_padrao()`
Retorna a impressora padrão do Windows.

```python
from utils.impressora import obter_impressora_padrao

impressora = obter_impressora_padrao()
print(impressora)
# 'EPSON TM-T20'
```

### `obter_impressora_configurada()`
Retorna a impressora configurada no `config.json` ou a padrão do sistema.

```python
from utils.impressora import obter_impressora_configurada

impressora = obter_impressora_configurada()
print(impressora)
```

### `obter_colunas_configuradas()`
Retorna o número de colunas configurado no `config.json`.

```python
from utils.impressora import obter_colunas_configuradas

colunas = obter_colunas_configuradas()
print(colunas)
# 32 (para papel 58mm) ou 42 (padrão 80mm)
```

### `imprimir_venda_por_codigo(cod_pedido)`
Busca os dados de uma venda no banco e imprime o cupom.

```python
from utils.impressora import imprimir_venda_por_codigo

sucesso = imprimir_venda_por_codigo("0000000123")
if sucesso:
    print("Impresso com sucesso!")
else:
    print("Erro ao imprimir")
```

### Classe `ImpressoraTermica`

Classe para impressão personalizada.

```python
from utils.impressora import ImpressoraTermica

# Inicializa a impressora (usa configurações do config.json)
impressora = ImpressoraTermica()

# Ou especifica a largura manualmente
impressora = ImpressoraTermica(width_cols=32)  # Para papel 58mm

# Adiciona linhas
impressora.adicionar_linha("Texto normal")
impressora.adicionar_linha("Texto centralizado", centralizar=True)
impressora.adicionar_linha("Texto em negrito", negrito=True)
impressora.adicionar_separador("-")

# Ou imprime um cupom completo
dados_venda = {
    "cod_pedido": "0000000123",
    "nome_cliente": "JOÃO DA SILVA",
    "endereco_cliente": "RUA DAS FLORES, N 123\nCENTRO - SAO PAULO/SP - CEP: 01234-567",
    "nome_vendedor": "MARIA SANTOS",
    "responsavel": "CARLOS SOUZA",
    "forma_pagamento": "1 - A Prazo",
    "data_emissao": "05/11/2025",
    "hora_emissao": "14:30:25",
    "valor_total": 150.00,
    "quantidade_total": 5.00,
    "itens": [
        {
            "descricao": "PRODUTO 1",
            "quantidade": 2.0,
            "valor_unitario": 50.0,
            "valor_total": 100.0
        },
        {
            "descricao": "PRODUTO 2",
            "quantidade": 1.0,
            "valor_unitario": 50.0,
            "valor_total": 50.0
        }
    ]
}

sucesso = impressora.imprimir_cupom_venda(dados_venda)
```

## 📐 Especificações Técnicas

- **Largura:** Configurável (20 a 80 colunas de caracteres)
  - Padrão: 42 colunas (papel 80mm)
  - Configurável via interface gráfica (campo "Colunas")
- **Codepage:** CP850 (Multilingual Latin I)
- **Quebra de linha:** `\r\n` (CR+LF)
- **Comandos ESC/POS utilizados:**
  - `ESC E 1` (0x1B 0x45 0x01) - Ativa negrito
  - `ESC E 0` (0x1B 0x45 0x00) - Desativa negrito
  - `GS ! 17` (0x1D 0x21 0x11) - Texto 2x (largura e altura)
  - `GS ! 0` (0x1D 0x21 0x00) - Texto normal
  - `GS V 1` (0x1D 0x56 0x01) - Corte parcial do papel

## 🗂️ Arquivos do Sistema

| Arquivo | Descrição |
|---------|-----------|
| `utils/impressora.py` | Módulo principal de impressão |
| `ui/database/logica_servidor.py` | Carrega impressoras na tela de configuração |
| `utils/websocket_server.py` | Rota WebSocket para impressão |
| `config.json` | Armazena a impressora configurada |

## ⚠️ Troubleshooting

### Impressora não aparece na lista
- Verifique se a impressora está instalada no Windows
- Reinicie o aplicativo após instalar a impressora

### Texto pulando para próxima linha / Quebras indesejadas
- **Causa:** O número de colunas está configurado maior que a largura real do papel
- **Solução:** 
  1. Abra Configurações do servidor
  2. Diminua o valor do campo **"Colunas"**
  3. Para papel 58mm (Epson): use **32 colunas**
  4. Para papel 80mm: use **42 colunas**
  5. Salve e teste novamente

### Erro ao imprimir
- Verifique se a impressora está ligada e conectada
- Verifique se há papel na impressora
- Teste a impressora com outro aplicativo

### Caracteres estranhos no cupom
- A impressora usa codepage CP850 (padrão para impressoras térmicas)
- Evite usar caracteres especiais complexos
- Se aparecer "V !" no início, verifique se a impressora está em modo RAW
- Acentuação pode não aparecer perfeitamente em todas as impressoras

### Cupom não corta automaticamente
- O sistema usa corte parcial (GS V 1)
- Nem todas as impressoras suportam o comando de corte
- Configure o corte automático nas configurações da impressora no Windows
- Se o problema persistir, você pode remover manualmente o papel

## 📝 Logs

O sistema registra logs de impressão no console:

```
✅ Cupom impresso com sucesso na impressora: EPSON TM-T20
🖨️ Recebido comando imprimir_venda via WebSocket
✅ Cupom do pedido 0000000123 impresso com sucesso
```

## 🔄 Integração com Mobile

Para integrar com o aplicativo mobile, basta enviar a requisição WebSocket após processar um pedido:

```javascript
// Após processar o pedido com sucesso
const imprimirVenda = {
  comando: "imprimir_venda",
  cod_pedido: "0000000123"
};

websocket.send(JSON.stringify(imprimirVenda));
```

---

**Desenvolvido para ICThUS Pocket Sync** 🐟

