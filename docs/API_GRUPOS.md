# API - Grupos de Produtos

## Endpoint
**Comando:** `get_grupos`

## Descrição
Este endpoint retorna a lista de grupos de produtos que possuem produtos ativos no estoque. Útil para criar filtros e carrosséis de grupos nas telas do aplicativo mobile.

## Formato da Requisição

```json
{
  "comando": "get_grupos"
}
```

Ou simplesmente como string:
```
get_grupos
```

## Formato da Resposta

### Sucesso

```json
{
  "grupos": [
    {
      "Código Grupo": "001",
      "Descrição Grupo": "CAPACETE"
    },
    {
      "Código Grupo": "002",
      "Descrição Grupo": "LUVAS"
    },
    {
      "Código Grupo": "003",
      "Descrição Grupo": "BOTAS"
    }
  ]
}
```

### Erro

```json
{
  "erro": "Mensagem de erro"
}
```

## Observações

1. **Filtro de Produtos Ativos**: Apenas grupos que possuem produtos ativos (`Ativo = 1`) são retornados.

2. **Ordenação**: Os grupos são ordenados alfabeticamente por `Descrição Grupo`.

3. **Uso com Filtro de Produtos**: Use o campo `Descrição Grupo` retornado em `get_produtos` para filtrar os produtos por grupo no frontend.

## Exemplo de Uso

### 1. Buscar lista de grupos
```json
{
  "comando": "get_grupos"
}
```

### 2. Buscar produtos e filtrar por grupo
```json
{
  "comando": "get_produtos"
}
```

Depois, no frontend, filtre os produtos onde `produto["Descrição Grupo"] === grupo_selecionado`.

## Implementação no Mobile

Para implementar o carrossel de grupos e filtro:

1. **Carregar grupos**: Chame `get_grupos` ao abrir a tela
2. **Exibir carrossel**: Mostre os grupos em um carrossel horizontal
3. **Filtrar produtos**: Ao clicar em um grupo, filtre os produtos localmente usando `Descrição Grupo`
4. **Opção "Todos"**: Adicione uma opção "Todos" no carrossel para mostrar todos os produtos

### Exemplo de Filtro (JavaScript/TypeScript)

```typescript
// Filtrar produtos por grupo
function filtrarProdutosPorGrupo(produtos: Produto[], grupo: string | null) {
  if (!grupo || grupo === "TODOS") {
    return produtos;
  }
  return produtos.filter(p => p["Descrição Grupo"] === grupo);
}
```

