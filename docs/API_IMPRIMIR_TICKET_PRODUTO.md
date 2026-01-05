# API - Imprimir Ticket de Produto

## Endpoint
**Comando:** `imprimir_ticket_produto`

## Descrição
Este endpoint permite imprimir tickets individuais de produtos. O ticket contém informações do produto, quantidade, valores, vendedor e observações. Pode ser enviado um único item ou uma lista de itens para impressão em lote.

## Formato da Requisição

### Enviar um único item

```json
{
  "comando": "imprimir_ticket_produto",
  "item": {
    "cod_item": "0000001",
    "quantidade": 2.5,
    "valor_unitario": 10.50,
    "cod_vendedor": "001",
    "cod_pedido": "0000000001",
    "descricao": "PRODUTO EXEMPLO",
    "nome_vendedor": "João Silva",
    "observacao": "Entregar na recepção"
  },
  "nome_impressora": "Impressora Térmica",
  "colunas": 42
}
```

### Enviar múltiplos itens (lista)

```json
{
  "comando": "imprimir_ticket_produto",
  "cod_vendedor": "001",
  "nome_vendedor": "João Silva",
  "itens": [
    {
      "cod_item": "0000001",
      "quantidade": 2.5,
      "valor_unitario": 10.50,
      "cod_pedido": "0000000001",
      "descricao": "PRODUTO EXEMPLO 1",
      "observacao": "Entregar na recepção"
    },
    {
      "cod_item": "0000002",
      "quantidade": 1.0,
      "valor_unitario": 25.00,
      "cod_pedido": "0000000001",
      "descricao": "PRODUTO EXEMPLO 2",
      "observacao": "Produto frágil"
    }
  ],
  "nome_impressora": "Impressora Térmica",
  "colunas": 42
}
```

**Nota:** Quando enviar múltiplos itens, você pode informar `cod_vendedor` e `nome_vendedor` no nível superior (como no exemplo acima). Nesse caso, não é necessário informar `cod_vendedor` em cada item. Os tickets serão impressos com separadores entre eles, e vendedor/hora aparecerão apenas no final.

## Parâmetros

### Campos Obrigatórios

**Para um único item:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `cod_item` | string | Código do item/produto |
| `quantidade` | number | Quantidade do produto |
| `valor_unitario` | number | Valor unitário do produto |
| `cod_vendedor` | string | Código do vendedor |
| `cod_pedido` | string | Código do pedido |

**Para múltiplos itens:**
- Se informar `cod_vendedor` no nível superior: cada item precisa apenas de `cod_item`, `quantidade`, `valor_unitario`, `cod_pedido`
- Se não informar `cod_vendedor` no nível superior: cada item precisa incluir `cod_vendedor` também

### Campos Opcionais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `descricao` | string | Descrição do produto. Se não for informado, será buscado no banco de dados |
| `nome_vendedor` | string | Nome do vendedor. Se não for informado, será buscado no banco de dados |
| `observacao` ou `Observacoes` | string | Observação do item (aceita ambos os formatos) |
| `nome_impressora` ou `impressora` | string | Nome da impressora a usar. Se não informado, usa a configurada no config.json |
| `colunas` | number | Número de colunas (20-80). Se não informado, usa o valor configurado no config.json |

## Formato da Resposta

### Sucesso (todos os tickets impressos)

```json
{
  "sucesso": true,
  "mensagem": "2 ticket(s) impresso(s) com sucesso",
  "total": 2,
  "resultados": [
    {
      "indice": 0,
      "sucesso": true,
      "mensagem": "Ticket do item 0000001 impresso com sucesso"
    },
    {
      "indice": 1,
      "sucesso": true,
      "mensagem": "Ticket do item 0000002 impresso com sucesso"
    }
  ],
  "impressora_usada": "Impressora Térmica",
  "colunas_usadas": 42
}
```

### Sucesso Parcial (alguns tickets impressos)

```json
{
  "sucesso": false,
  "mensagem": "Alguns tickets foram impressos. 1 de 2 com sucesso",
  "total": 2,
  "resultados": [
    {
      "indice": 0,
      "sucesso": true,
      "mensagem": "Ticket do item 0000001 impresso com sucesso"
    },
    {
      "indice": 1,
      "sucesso": false,
      "erro": "Falha ao imprimir ticket do item 0000002"
    }
  ],
  "impressora_usada": "Impressora Térmica",
  "colunas_usadas": 42
}
```

### Erro

```json
{
  "sucesso": false,
  "erro": "É necessário enviar 'item' ou 'itens' (lista)"
}
```

## Formato do Ticket Impresso

### Ticket único

O ticket será impresso com o seguinte formato:

```
========================================
        NOME DA EMPRESA
========================================

QUANTIDADE: 2.50

    PRODUTO EXEMPLO
    (em letra maior)

Entregar na recepção

Hora: 14:30:25
Vendedor: João Silva
```

### Múltiplos tickets

Quando enviar múltiplos itens, os tickets serão impressos em sequência com separadores:

```
========================================
        NOME DA EMPRESA
========================================

QUANTIDADE: 2.50

    PRODUTO EXEMPLO 1
    (em letra maior)

Entregar na recepção

----------------------------------------

QUANTIDADE: 1.00

    PRODUTO EXEMPLO 2
    (em letra maior)

Produto frágil

========================================

Hora: 14:30:25
Vendedor: João Silva
```

Note que vendedor e hora aparecem apenas uma vez no final quando houver múltiplos itens.

## Observações Importantes

1. **Campo de Observação**: O sistema aceita tanto `observacao` quanto `Observacoes` (com acento) para compatibilidade.

2. **Descrição e Vendedor**: Se `descricao` ou `nome_vendedor` não forem informados, o sistema buscará automaticamente no banco de dados usando o `cod_item` e `cod_vendedor` respectivamente.

3. **Impressora**: Se `nome_impressora` não for informado, o sistema usará a impressora configurada no arquivo `config.json`. Se a impressora informada não existir, retornará erro.

4. **Colunas**: O número de colunas deve estar entre 20 e 80. Se não for informado, usa o valor configurado no `config.json`.

5. **Impressão em Lote**: Ao enviar múltiplos itens, cada item será impresso em um ticket separado. O sistema retornará o resultado de cada impressão individualmente.

6. **Validação**: Todos os campos obrigatórios devem estar presentes em cada item. Se algum item estiver com campos faltando, apenas aquele item falhará, mas os outros serão processados.

## Exemplos de Uso

### Exemplo 1: Imprimir um único ticket

```json
{
  "comando": "imprimir_ticket_produto",
  "item": {
    "cod_item": "0000001",
    "quantidade": 3,
    "valor_unitario": 15.90,
    "cod_vendedor": "001",
    "cod_pedido": "0000000005",
    "observacao": "Produto perecível"
  }
}
```

### Exemplo 2: Imprimir múltiplos tickets com impressora específica

```json
{
  "comando": "imprimir_ticket_produto",
  "itens": [
    {
      "cod_item": "0000001",
      "quantidade": 2,
      "valor_unitario": 10.00,
      "cod_vendedor": "001",
      "cod_pedido": "0000000005"
    },
    {
      "cod_item": "0000002",
      "quantidade": 1,
      "valor_unitario": 25.50,
      "cod_vendedor": "001",
      "cod_pedido": "0000000005",
      "observacao": "Fragil"
    }
  ],
  "nome_impressora": "XP-80C"
}
```

### Exemplo 3: Usando Observacoes (com acento)

```json
{
  "comando": "imprimir_ticket_produto",
  "item": {
    "cod_item": "0000001",
    "quantidade": 1,
    "valor_unitario": 50.00,
    "cod_vendedor": "001",
    "cod_pedido": "0000000005",
    "Observacoes": "Entregar até as 18h"
  }
}
```

