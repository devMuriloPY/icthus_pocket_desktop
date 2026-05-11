import asyncio
import websockets
import json
import threading
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal

from utils.sqlserver import conexao_ativa
from utils.config import criar_settings  # ✅ Config JSON
from utils.impressora import imprimir_venda_por_codigo, listar_impressoras_windows, imprimir_ticket_produto, imprimir_tickets_produtos_multiplos

def obter_porta_websocket(padrao=5757):
    """Lê a porta configurada no config.json, ou usa a padrão."""
    settings = criar_settings()
    porta_str = settings.value("porta", str(padrao))
    try:
        return int(porta_str)
    except (ValueError, TypeError):
        return padrao


def obter_linha_separada_mesmo_item():
    """Mesma preferência da checkbox na tela de servidor (config JSON)."""
    settings = criar_settings()
    v = settings.value("linha_separada_mesmo_item", False)
    if isinstance(v, str):
        return v.lower() in ("true", "1", "yes")
    return bool(v)


def expandir_itens_linha_separada(itens):
    """
    Com a opção ativa, cada item com Quantidade > 1 inteira vira N linhas:
    Quantidade 1, mesmo ValorUnitario, ValorTotal = ValorUnitario (por linha).
    Quantidades fracionárias não são divididas (mantém 1 linha).
    """
    if not itens or not obter_linha_separada_mesmo_item():
        return itens
    resultado = []
    for item in itens:
        qtd = float(item.get("Quantidade", 0))
        if qtd <= 1:
            resultado.append(item)
            continue
        n = int(round(qtd))
        if abs(qtd - n) > 1e-6:
            resultado.append(item)
            continue
        vu = float(item["ValorUnitario"])
        for _ in range(n):
            linha = dict(item)
            linha["Quantidade"] = 1
            linha["ValorUnitario"] = vu
            linha["ValorTotal"] = vu
            resultado.append(linha)
    return resultado

async def processar_conexao(websocket):
    """Processa os comandos recebidos via WebSocket."""
    try:
        async for mensagem in websocket:
            try:
                # Tenta parsear como JSON
                dados = json.loads(mensagem)
                comando = dados.get("comando", mensagem)
                
                if comando == "get_produtos":
                    await enviar_lista_produtos(websocket)
                elif comando == "get_clientes":
                    await enviar_lista_clientes(websocket)
                elif comando == "get_vendedores":
                    await enviar_lista_vendedores(websocket)
                elif comando == "get_cidades":
                    await enviar_lista_cidades(websocket)
                elif comando == "processar_pedido":
                    await processar_pedido(websocket, dados)
                elif comando == "cadastrar_cliente":
                    await cadastrar_cliente(websocket, dados)
                elif comando == "imprimir_venda":
                    await imprimir_venda(websocket, dados)
                elif comando == "consultar_status_pedidos":
                    await consultar_status_pedidos(websocket, dados)
                elif comando == "inserir_item_pedido_existente":
                    await inserir_item_pedido_existente(websocket, dados)
                elif comando == "listar_impressoras":
                    await listar_impressoras(websocket)
                elif comando == "imprimir_ticket_produto":
                    await imprimir_ticket_produto_ws(websocket, dados)
                elif comando == "listar_pedidos_mobile":
                    await listar_pedidos_mobile(websocket)
                elif comando == "alterar_pedido":
                    await alterar_pedido(websocket, dados)
                else:
                    await websocket.send(json.dumps({"erro": "comando inválido"}))
            except json.JSONDecodeError:
                # Se não for JSON, trata como comando string simples
                if mensagem == "get_produtos":
                    await enviar_lista_produtos(websocket)
                elif mensagem == "get_clientes":
                    await enviar_lista_clientes(websocket)
                elif mensagem == "get_vendedores":
                    await enviar_lista_vendedores(websocket)
                elif mensagem == "get_cidades":
                    await enviar_lista_cidades(websocket)
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
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT [Código Item], [Descrição Item], 
            [Preço Unitário], [Código Barras], [Estoque Previsto], [Código Saída], [Descrição Grupo]
            FROM Estoque 
            LEFT JOIN [Grupos] g ON g.[Código Grupo] = Estoque.[Código Grupo]
            WHERE Ativo = 1
        """)
        produtos = [
            {
                "Código Item": row[0],
                "Descrição Item": row[1],
                "Preço Unitário": float(row[2]),
                "Código Barras": row[3],
                "Estoque Previsto": float(row[4]),
                "Código Saída": row[5],
                "Descrição Grupo": row[6] if row[6] else None
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        await websocket.send(json.dumps({"produtos": produtos}))
    except Exception as e:
        await websocket.send(json.dumps({"erro": str(e)}))

async def enviar_lista_clientes(websocket):
    """Executa a consulta no banco e envia os clientes."""
    try:
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                [Código Cliente],
                [Apelido] as Fantasia,
                [Nome Cliente] as [Razão Social],
                Endereço,
                Bairro,
                Número,
                Cidade,
                Estado,
                CEP,
                CASE WHEN FJ = 'F' THEN CPF ELSE CNPJ END as [CPF / CNPJ],
                Celular,
                Telefone,
                Inativo
            FROM CLIENTES
            ORDER BY [Código Cliente]
        """)
        clientes = [
            {
                "Código Cliente": row[0],
                "Fantasia": row[1],
                "Razão Social": row[2],
                "Endereço": row[3],
                "Bairro": row[4],
                "Número": row[5],
                "Cidade": row[6],
                "Estado": row[7],
                "CEP": row[8],
                "CPF / CNPJ": row[9],
                "Celular": row[10],
                "Telefone": row[11],
                "Inativo": row[12]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        await websocket.send(json.dumps({"clientes": clientes}))
    except Exception as e:
        await websocket.send(json.dumps({"erro": str(e)}))

async def enviar_lista_vendedores(websocket):
    """Executa a consulta no banco e envia os vendedores."""
    try:
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                [Código Funcionário] as [Código Vendedor],
                [Nome Funcionário]
            FROM Funcionários
            WHERE Ativo = 1 AND Vendedor = 1
        """)
        vendedores = [
            {
                "Código Vendedor": row[0],
                "Nome Funcionário": row[1]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        await websocket.send(json.dumps({"vendedores": vendedores}))
    except Exception as e:
        await websocket.send(json.dumps({"erro": str(e)}))

async def enviar_lista_cidades(websocket):
    """Executa a consulta no banco e envia as cidades."""
    try:
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Cidade, Estado, [Código Cidade] 
            FROM Cidades 
            ORDER BY Estado, Cidade
        """)
        cidades = [
            {
                "Cidade": row[0],
                "Estado": row[1],
                "Código Cidade": row[2]
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        await websocket.send(json.dumps({"cidades": cidades}))
    except Exception as e:
        await websocket.send(json.dumps({"erro": str(e)}))

def gerar_hash_pedido(pedido, itens):
    """Gera um hash único do pedido baseado nos dados principais para detectar duplicações.
    
    O hash é baseado em:
    - Código do vendedor
    - Código do cliente
    - Lista de itens (código, quantidade, valor unitário)
    - Valor total
    - Responsável (se houver)
    - Forma de pagamento mobile (se houver)
    """
    # Ordena os itens para garantir consistência
    itens_ordenados = sorted(itens, key=lambda x: (
        str(x.get("CodItem", "")),
        float(x.get("Quantidade", 0)),
        float(x.get("ValorUnitario", 0))
    ))
    
    # Monta uma string com os dados principais do pedido
    dados_hash = []
    dados_hash.append(f"vendedor:{pedido.get('CodVendedor', '')}")
    dados_hash.append(f"cliente:{pedido.get('CodCliente', '')}")
    dados_hash.append(f"total:{pedido.get('ValorTotal', 0)}")
    dados_hash.append(f"responsavel:{pedido.get('Responsavel', '')}")
    dados_hash.append(f"forma_pagamento:{pedido.get('FormaPagamento', '')}")
    
    # Adiciona os itens ordenados
    for item in itens_ordenados:
        dados_hash.append(f"item:{item.get('CodItem', '')}:qtd:{item.get('Quantidade', 0)}:valor:{item.get('ValorUnitario', 0)}")
    
    # Gera o hash MD5
    string_hash = "|".join(dados_hash)
    hash_obj = hashlib.md5(string_hash.encode('utf-8'))
    return hash_obj.hexdigest()

async def processar_pedido(websocket, dados):
    """Recebe um pedido com seus itens e insere no banco."""
    try:
        
        # Extrai dados do pedido
        pedido = dados.get("pedido")
        itens = dados.get("itens", [])
        
        if not pedido or not itens:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Pedido e itens são obrigatórios"
            }))
            return
        
        # Valida campos obrigatórios do pedido (CodCliente é opcional agora)
        campos_obrigatorios = ["CodVendedor", "ValorTotal", "ValorProdutos", "QuantidadeProdutos"]
        for campo in campos_obrigatorios:
            if campo not in pedido:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Campo obrigatório ausente: {campo}"
                }))
                return

        itens = expandir_itens_linha_separada(itens)
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Inicia transação com isolamento SERIALIZABLE para evitar race conditions
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cursor.execute("BEGIN TRANSACTION")
            
            # Verifica se o cliente foi informado, senão busca o cliente padrão
            if not pedido.get("CodCliente") or pedido.get("CodCliente") in [None, "", "null"]:
                cliente_padrao = obter_cliente_padrao(cursor)
                pedido["CodCliente"] = cliente_padrao
            
            # Verifica se já existe um pedido duplicado recente (últimos 10 minutos)
            # Usa UPDLOCK e HOLDLOCK para garantir que apenas uma thread processe por vez
            # Isso evita race conditions quando dois pedidos chegam simultaneamente
            data_limite = datetime.now() - timedelta(minutes=10)
            
            # Primeiro, tenta encontrar pedidos com mesmo vendedor, cliente e valor total
            # O lock garante que apenas uma requisição processe por vez
            cursor.execute("""
                SELECT TOP 1 P.[Código Pedido]
                FROM Pedidos P WITH (UPDLOCK, HOLDLOCK, ROWLOCK)
                WHERE P.[Origem Venda] = '3 - Mobile'
                  AND P.[Data Cadastro] >= ?
                  AND P.[Código Vendedor] = ?
                  AND P.[Código Cliente] = ?
                  AND ABS(P.[Valor Total] - ?) < 0.01
                  AND P.Fechado = 0
                  AND P.Entregue = 0
                  AND P.Parcelado = 0
                ORDER BY P.[Data Cadastro] DESC, P.[Código Pedido] DESC
            """, data_limite, pedido["CodVendedor"], pedido["CodCliente"], float(pedido["ValorTotal"]))
            
            pedido_duplicado = cursor.fetchone()
            
            # Log para debug
            if pedido_duplicado:
                print(f"🔍 Verificando possível duplicação: pedido {pedido_duplicado[0]} encontrado")
            else:
                print(f"✅ Nenhum pedido duplicado encontrado para vendedor {pedido['CodVendedor']}, cliente {pedido['CodCliente']}, valor {pedido['ValorTotal']}")
            
            if pedido_duplicado:
                cod_pedido_existente = pedido_duplicado[0]
                
                # Verifica se os itens também são iguais (comparação detalhada)
                cursor.execute("""
                    SELECT [Código Item], CAST(Quantidade AS FLOAT) as Quantidade, 
                           CAST([Valor Unitário] AS FLOAT) as ValorUnitario,
                           CAST([Valor Total] AS FLOAT) as ValorTotal
                    FROM [Pedidos Itens]
                    WHERE [Código Pedido] = ?
                    ORDER BY [Código Item], Quantidade, [Valor Unitário]
                """, cod_pedido_existente)
                
                itens_existentes = cursor.fetchall()
                
                # Ordena os itens do pedido atual para comparação
                itens_atual_ordenados = sorted(
                    [(item.get("CodItem"), float(item.get("Quantidade", 0)), 
                      float(item.get("ValorUnitario", 0)), float(item.get("ValorTotal", 0))) 
                     for item in itens],
                    key=lambda x: (x[0], x[1], x[2])
                )
                
                # Compara quantidade de itens
                if len(itens_existentes) == len(itens_atual_ordenados):
                    # Compara cada item
                    itens_iguais = True
                    for i, item_existente in enumerate(itens_existentes):
                        item_atual = itens_atual_ordenados[i]
                        if (item_existente[0] != item_atual[0] or  # Código do item
                            abs(item_existente[1] - item_atual[1]) >= 0.01 or  # Quantidade
                            abs(item_existente[2] - item_atual[2]) >= 0.01):  # Valor unitário
                            itens_iguais = False
                            break
                    
                    if itens_iguais:
                        # Pedido duplicado encontrado - retorna o pedido existente
                        cursor.execute("COMMIT TRANSACTION")
                        await websocket.send(json.dumps({
                            "sucesso": True,
                            "mensagem": f"Pedido duplicado detectado. Retornando pedido existente {cod_pedido_existente}",
                            "cod_pedido": cod_pedido_existente,
                            "total_itens": len(itens_existentes),
                            "duplicado": True
                        }))
                        return
            
            # Gera o próximo código de pedido
            cod_pedido = gerar_proximo_codigo_pedido(cursor)
            pedido["CodPedido"] = cod_pedido
            
            
            # Insere o pedido
            inserir_pedido(cursor, pedido)
            
            # Insere os itens do pedido
            for item in itens:
                inserir_item_pedido(cursor, pedido["CodPedido"], item, pedido["CodVendedor"])
            
            cursor.execute("COMMIT TRANSACTION")
            conn.commit()
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"Pedido {pedido['CodPedido']} processado com sucesso",
                "cod_pedido": pedido["CodPedido"],
                "total_itens": len(itens)
            }))
            
            
        except Exception as e:
            try:
                cursor.execute("ROLLBACK TRANSACTION")
            except:
                pass
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Erro ao processar pedido: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

def obter_cliente_padrao(cursor):
    """Busca o código do cliente padrão (à vista) na tabela opções."""
    try:
        cursor.execute("SELECT [Código Cliente à Vista] as [Cliente Padrão] FROM opções")
        row = cursor.fetchone()
        
        if row and row[0]:
            return row[0]
        else:
            raise Exception("Cliente padrão não encontrado na tabela opções")
    except Exception as e:
        raise Exception(f"Erro ao buscar cliente padrão: {str(e)}")

def gerar_proximo_codigo_pedido(cursor):
    """Gera o próximo código de pedido baseado no último código do banco."""
    try:
        cursor.execute("""
            SELECT TOP (1) 
                RIGHT('0000000000' + CAST(CAST([Código Pedido] AS INT) + 1 AS VARCHAR(10)), 10)
            FROM Pedidos 
            ORDER BY [Código Pedido] DESC
        """)
        row = cursor.fetchone()
        
        if row and row[0]:
            return row[0]
        else:
            # Se não houver nenhum pedido, retorna o primeiro código
            return "0000000001"
    except Exception as e:
        # Em caso de erro ou tabela vazia, começa do primeiro
        print(f"⚠️ Aviso ao gerar código de pedido: {e}, usando 0000000001")
        return "0000000001"

def converter_documento_venda(doc_venda):
    """
    Converte o documento de venda para o formato correto.
    Aceita: 1, '1', '1 - Pedido' -> retorna '1 - Pedido'
    Aceita: 2, '2', '2 - Orçamento' -> retorna '2 - Orçamento'
    Aceita: 3, '3', '3 - Condicional' -> retorna '3 - Condicional'
    """
    if doc_venda is None:
        return '1 - Pedido'
    
    # Converte para string
    doc_str = str(doc_venda).strip()
    
    # Mapeamento de conversão
    mapa_documentos = {
        '1': '1 - Pedido',
        '2': '2 - Orçamento',
        '3': '3 - Condicional',
        '1 - Pedido': '1 - Pedido',
        '2 - Orçamento': '2 - Orçamento',
        '3 - Condicional': '3 - Condicional',
        '1 - PEDIDO': '1 - Pedido',
        '2 - ORCAMENTO': '2 - Orçamento',
        '3 - CONDICIONAL': '3 - Condicional',
        '1 - pedido': '1 - Pedido',
        '2 - orcamento': '2 - Orçamento',
        '3 - condicional': '3 - Condicional',
    }
    
    # Retorna o documento convertido ou o próprio valor se não estiver no mapa
    return mapa_documentos.get(doc_str, doc_str)

def inserir_pedido(cursor, pedido):
    """Insere o pedido no banco de dados."""
    
    # Variáveis automáticas
    data_emissao = datetime.now().date()
    hora_emissao = datetime.now().time()
    origem_venda = '3 - Mobile'
    forma_pagamento = '1 - À Prazo'
    codigo_cc = '001'
    data_cadastro = datetime.now().date()
    cadastrado = 'MOBILE'
    data_atualizacao = datetime.now()
    atualizado = 'MOBILE'
    
    # Campos opcionais que podem ser recebidos via WebSocket
    documento_venda_raw = pedido.get("DocumentoVenda", '1 - Pedido')
    documento_venda = converter_documento_venda(documento_venda_raw)
    responsavel = pedido.get("Responsavel", None)
    forma_pagamento_mobile = pedido.get("FormaPagamento", None)  # Forma de pagamento do mobile
    
    sql = """
    INSERT INTO Pedidos (
        [Código Pedido], [Código Cliente],
        [Data Emissão], [Hora Emissão],
        [Documento Venda], [Código Vendedor],
        [Valor Total], [Valor Produtos], [Valor Total Bruto],
        [Origem Venda], [Forma Pagamento],
        [Código CC], [Quantidade Produtos],
        Ok, [Código Empresa], [Data Cadastro],
        Cadastrado, [Data Atualização],
        Atualizado, Responsável, [Forma Pagamento Mobile]
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(sql,
        pedido["CodPedido"],
        pedido["CodCliente"],
        data_emissao,
        hora_emissao,
        documento_venda,
        pedido["CodVendedor"],
        pedido["ValorTotal"],
        pedido["ValorProdutos"],
        pedido["ValorTotal"],
        origem_venda,
        forma_pagamento,
        codigo_cc,
        pedido["QuantidadeProdutos"],
        1,  # Ok
        1,  # Código Empresa
        data_cadastro,
        cadastrado,
        data_atualizacao,
        atualizado,
        responsavel,  # Responsável (opcional)
        forma_pagamento_mobile  # Forma Pagamento Mobile (opcional)
    )

def inserir_item_pedido(cursor, cod_pedido, item, cod_vendedor):
    """Insere um item do pedido com controle de sequência."""
    
    # Valida campos obrigatórios do item
    campos_obrigatorios = ["CodItem", "Quantidade", "ValorUnitario", "ValorTotal"]
    for campo in campos_obrigatorios:
        if campo not in item:
            raise ValueError(f"Campo obrigatório ausente no item: {campo}")
    
    # Variáveis automáticas
    data_cadastro = datetime.now().date()
    cadastrado = 'MOBILE'
    data_atualizacao = datetime.now()
    atualizado = 'MOBILE'
    estacao = item.get("Estacao", "MOBILE")
    
    # Controle de sequência inline
    cursor.execute("SET XACT_ABORT ON")
    cursor.execute("SET NOCOUNT ON")
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    
    # 1) Garante a linha de controle do pedido
    cursor.execute("""
        IF NOT EXISTS (
            SELECT 1
            FROM [SYS~Sequencial] WITH (UPDLOCK, HOLDLOCK)
            WHERE [SYS~Chave] = ?
              AND [SYS~Tabela] = 'Pedidos Itens'
              AND [SYS~Campo] = 'SEQ'
        )
        BEGIN
            INSERT INTO [SYS~Sequencial]
                ([SYS~BD], [SYS~Tabela], [SYS~Campo], [SYS~Chave],
                 [SYS~Valor], [SYS~ValorAnterior], [SYS~Estacao],
                 [SYS~Identificacao], [SYS~Pendentes])
            VALUES
                ('WM', 'Pedidos Itens', 'SEQ', ?,
                 0, 0, ?, '1671179755,29169', 0)
        END
    """, cod_pedido, cod_pedido, estacao)
    
    # 2) Incrementa e captura o novo valor de sequência
    cursor.execute("""
        UPDATE S WITH (UPDLOCK, HOLDLOCK)
        SET [SYS~ValorAnterior] = TRY_CAST(S.[SYS~Valor] AS INT),
            [SYS~Valor] = TRY_CAST(S.[SYS~Valor] AS INT) + 1,
            [SYS~Pendentes] = TRY_CAST(S.[SYS~Valor] AS INT) + 1,
            [SYS~Estacao] = ?,
            [SYS~Identificacao] = '1671179755,29169'
        OUTPUT inserted.[SYS~Valor]
        FROM [SYS~Sequencial] AS S
        WHERE S.[SYS~Chave] = ?
          AND S.[SYS~Tabela] = 'Pedidos Itens'
          AND S.[SYS~Campo] = 'SEQ'
    """, estacao, cod_pedido)
    
    # Captura o novo valor de SEQ
    row = cursor.fetchone()
    if row:
        seq_int = int(row[0])
        seq_formatado = str(seq_int).zfill(7)
    else:
        raise Exception("Falha ao gerar SEQ para o item do pedido")
    
    # Obtém observações do item (opcional)
    observacoes = item.get("Observacoes", None)
    
    # 3) Insere o item com o SEQ calculado
    sql = """
    INSERT INTO [Pedidos Itens] (
        [Código Pedido], SEQ, [Código Item], [Código Vendedor],
        Quantidade, [Valor Unitário], [Valor Total],
        [Tipo Item], [Preço Sugerido], [Valor Unitário Bruto],
        [Valor Total Bruto], Pendente, Ok,
        Item, [Quantidade Atacado], [Data Cadastro],
        Cadastrado, [Data Atualização], Atualizado, Observações
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(sql,
        cod_pedido,
        seq_formatado,
        item["CodItem"],
        cod_vendedor,  # Código Vendedor
        item["Quantidade"],
        item["ValorUnitario"],
        item["ValorTotal"],
        'P',  # Tipo Item
        item["ValorUnitario"],  # Preço Sugerido
        item["ValorUnitario"],  # Valor Unitário Bruto
        item["ValorTotal"],  # Valor Total Bruto
        1,  # Pendente
        1,  # Ok
        item["CodItem"],  # Item
        item["Quantidade"],  # Quantidade Atacado
        data_cadastro,
        cadastrado,
        data_atualizacao,
        atualizado,
        observacoes  # Observações
    )

def calcular_totais_pedido(cursor, cod_pedido):
    """Calcula os totais do pedido baseado nos itens."""
    cursor.execute("""
        SELECT 
            ISNULL(SUM([Valor Total]), 0) as ValorTotal,
            ISNULL(SUM([Valor Total]), 0) as ValorProdutos,
            ISNULL(SUM(Quantidade), 0) as QuantidadeProdutos
        FROM [Pedidos Itens]
        WHERE [Código Pedido] = ?
    """, cod_pedido)
    
    row = cursor.fetchone()
    if row:
        return {
            "ValorTotal": Decimal(str(row[0])),
            "ValorProdutos": Decimal(str(row[1])),
            "QuantidadeProdutos": Decimal(str(row[2]))
            }
    else:
        return {
            "ValorTotal": Decimal('0'),
            "ValorProdutos": Decimal('0'),
            "QuantidadeProdutos": Decimal('0')
        }

def atualizar_totais_pedido(cursor, cod_pedido):
    """Atualiza os totais do pedido na tabela Pedidos baseado nos itens."""
    # Calcula os novos totais
    totais = calcular_totais_pedido(cursor, cod_pedido)
    
    # Variáveis automáticas
    data_atualizacao = datetime.now()
    atualizado = 'MOBILE'
    
    # Atualiza o pedido
    sql = """
    UPDATE Pedidos
    SET [Valor Total] = ?,
        [Valor Produtos] = ?,
        [Valor Total Bruto] = ?,
        [Quantidade Produtos] = ?,
        [Data Atualização] = ?,
        Atualizado = ?
    WHERE [Código Pedido] = ?
    """
    
    cursor.execute(sql,
        totais["ValorTotal"],
        totais["ValorProdutos"],
        totais["ValorTotal"],  # Valor Total Bruto = Valor Total
        totais["QuantidadeProdutos"],
        data_atualizacao,
        atualizado,
        cod_pedido
    )
    
    return totais

async def inserir_item_pedido_existente(websocket, dados):
    """Insere um item em um pedido já existente e atualiza os totais do pedido."""
    try:
        
        # Extrai dados
        cod_pedido = dados.get("cod_pedido")
        item = dados.get("item")
        
        if not cod_pedido:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Código do pedido é obrigatório"
            }))
            return
        
        if not item:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Dados do item são obrigatórios"
            }))
            return
        
        # Valida campos obrigatórios do item
        campos_obrigatorios = ["CodItem", "Quantidade", "ValorUnitario", "ValorTotal"]
        for campo in campos_obrigatorios:
            if campo not in item:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Campo obrigatório ausente no item: {campo}"
                }))
                return

        itens_inserir = expandir_itens_linha_separada([item])
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Verifica se o pedido existe
            cursor.execute("""
                SELECT [Código Pedido], [Código Vendedor]
                FROM Pedidos
                WHERE [Código Pedido] = ?
            """, cod_pedido)
            
            row = cursor.fetchone()
            if not row:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Pedido {cod_pedido} não encontrado"
                }))
                return
            
            cod_vendedor = row[1]
            
            for linha in itens_inserir:
                inserir_item_pedido(cursor, cod_pedido, linha, cod_vendedor)
            
            # Atualiza os totais do pedido
            totais = atualizar_totais_pedido(cursor, cod_pedido)
            
            conn.commit()
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"Item inserido no pedido {cod_pedido} com sucesso",
                "cod_pedido": cod_pedido,
                "linhas_inseridas": len(itens_inserir),
                "totais_atualizados": {
                    "ValorTotal": float(totais["ValorTotal"]),
                    "ValorProdutos": float(totais["ValorProdutos"]),
                    "QuantidadeProdutos": float(totais["QuantidadeProdutos"])
                }
            }))
            
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Erro ao inserir item no pedido existente: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def cadastrar_cliente(websocket, dados):
    """Recebe os dados de um cliente e insere no banco."""
    try:
        
        # Extrai dados do cliente
        cliente = dados.get("cliente")
        
        if not cliente:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Dados do cliente são obrigatórios"
            }))
            return
        
        # Valida campos obrigatórios
        campos_obrigatorios = ["NomeCliente", "CodigoFuncionario", "Endereco", "Numero", 
                              "Bairro", "CodigoCidade", "Celular", "Email"]
        for campo in campos_obrigatorios:
            if campo not in cliente or not cliente[campo]:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Campo obrigatório ausente ou vazio: {campo}"
                }))
                return
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Processa os dados do cliente
            nome_cliente = str(cliente["NomeCliente"]).upper()
            codigo_funcionario = cliente["CodigoFuncionario"]
            endereco = str(cliente["Endereco"]).upper()
            numero = cliente["Numero"]
            bairro = str(cliente["Bairro"]).upper()
            codigo_cidade = cliente["CodigoCidade"]
            celular_raw = cliente["Celular"]
            email = str(cliente["Email"]).lower()
            cep_raw = cliente.get("CEP", None)
            cpf_raw = cliente.get("CPF", None)
            cnpj_raw = cliente.get("CNPJ", None)
            
            # Formata o celular: (XX)XXXXX-XXXX
            celular = formatar_celular(celular_raw)
            
            # Formata CEP ou usa o da empresa
            if cep_raw:
                cep = formatar_cep(cep_raw)
            else:
                cursor.execute("SELECT TOP 1 CEP FROM Empresas")
                row = cursor.fetchone()
                cep = row[0] if row and row[0] else None
            
            # Formata CPF e CNPJ
            cpf = formatar_cpf(cpf_raw) if cpf_raw else None
            cnpj = formatar_cnpj(cnpj_raw) if cnpj_raw else None
            
            # Determina se é Pessoa Física ou Jurídica
            fj = 'J' if cnpj else 'F'
            regime_fiscal = 'S - Simples Nacional' if cnpj else 'F - Pessoa Física'
            
            # Gera o próximo código de cliente
            cod_cliente = gerar_proximo_codigo_cliente(cursor)
            
            # Busca dados da cidade
            cursor.execute("""
                SELECT 
                    ISNULL([Cidade], (SELECT TOP 1 CIDADE FROM Empresas)),
                    ISNULL(Estado, (SELECT TOP 1 Estado FROM Empresas))
                FROM Cidades
                WHERE [Código Cidade] = ?
            """, codigo_cidade)
            row = cursor.fetchone()
            if row:
                cidade = row[0]
                estado = row[1]
            else:
                raise Exception(f"Cidade com código {codigo_cidade} não encontrada")
            
            # Define país padrão
            pais = 'BRASIL'
            codigo_pais = '1058'
            
            # Busca primeiro nome do funcionário
            cursor.execute("""
                SELECT LEFT([Nome Funcionário], CHARINDEX(' ', [Nome Funcionário] + ' ') - 1)
                FROM Funcionários 
                WHERE [Código Funcionário] = ?
            """, codigo_funcionario)
            row = cursor.fetchone()
            if row:
                nome_funcionario = row[0]
            else:
                raise Exception(f"Funcionário com código {codigo_funcionario} não encontrado")
            
            # Data/hora atual
            data_cadastro = datetime.now()
            
            # Insere o cliente
            sql = """
            INSERT INTO [Clientes]
            ([Nome Cliente], [Código Cliente], FJ, [Regime Fiscal Destinatário],
             [Endereço], Número, Bairro, Cidade, Estado, País, CEP,
             [Código Cidade], [Código País], [Celular], CPF, CNPJ, Email,
             Cadastrado, [Data Cadastro], Atualizado, [Data Atualização])
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(sql,
                nome_cliente,
                cod_cliente,
                fj,
                regime_fiscal,
                endereco,
                numero,
                bairro,
                cidade,
                estado,
                pais,
                cep,
                codigo_cidade,
                codigo_pais,
                celular,
                cpf,
                cnpj,
                email,
                nome_funcionario,
                data_cadastro,
                nome_funcionario,
                data_cadastro
            )
            
            # Atualiza SYS~Sequencial
            cursor.execute("""
                UPDATE [SYS~Sequencial] 
                SET [SYS~Valor] = CAST(? AS INT),
                    [SYS~ValorAnterior] = CAST(? AS INT) - 1,
                    [SYS~Estacao] = 'MOBILE'
                WHERE [SYS~Tabela] = 'Clientes'
            """, cod_cliente, cod_cliente)
            
            conn.commit()
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"Cliente {nome_cliente} cadastrado com sucesso",
                "cod_cliente": cod_cliente
            }))
            
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Erro ao cadastrar cliente: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

def gerar_proximo_codigo_cliente(cursor):
    """Gera o próximo código de cliente baseado no último código do banco."""
    try:
        cursor.execute("""
            SELECT TOP (1) 
                RIGHT('0000000' + CAST(CAST([Código Cliente] AS INT) + 1 AS VARCHAR(7)), 7)
            FROM Clientes 
            ORDER BY [Código Cliente] DESC
        """)
        row = cursor.fetchone()
        
        if row and row[0]:
            return row[0]
        else:
            # Se não houver nenhum cliente, retorna o primeiro código
            return "0000001"
    except Exception as e:
        print(f"⚠️ Aviso ao gerar código de cliente: {e}, usando 0000001")
        return "0000001"

def formatar_celular(celular):
    """Formata celular para o padrão (XX)XXXXX-XXXX."""
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(celular)))
    
    # Formata: (XX)XXXXX-XXXX
    if len(numeros) >= 10:
        return f"({numeros[0:2]}){numeros[2:7]}-{numeros[7:11]}"
    else:
        return celular

def formatar_cep(cep):
    """Formata CEP para o padrão XXXXX-XXX."""
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(cep)))
    
    # Formata: XXXXX-XXX
    if len(numeros) == 8:
        return f"{numeros[0:5]}-{numeros[5:8]}"
    else:
        return cep

def formatar_cpf(cpf):
    """Formata CPF para o padrão XXX.XXX.XXX-XX."""
    if not cpf:
        return None
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(cpf)))
    
    # Formata: XXX.XXX.XXX-XX
    if len(numeros) == 11:
        return f"{numeros[0:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:11]}"
    else:
        return cpf

def formatar_cnpj(cnpj):
    """Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX."""
    if not cnpj:
        return None
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(cnpj)))
    
    # Formata: XX.XXX.XXX/XXXX-XX
    if len(numeros) == 14:
        return f"{numeros[0:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:14]}"
    else:
        return cnpj

async def listar_impressoras(websocket):
    """Retorna a lista de impressoras disponíveis no sistema."""
    try:
        
        impressoras = listar_impressoras_windows()
        
        await websocket.send(json.dumps({
            "sucesso": True,
            "impressoras": impressoras,
            "total": len(impressoras)
        }))
        
        
    except Exception as e:
        print(f"❌ Erro ao listar impressoras: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def imprimir_venda(websocket, dados):
    """Recebe o código do pedido e imprime o cupom de venda."""
    try:
        
        # Extrai o código do pedido
        cod_pedido = dados.get("cod_pedido")
        
        if not cod_pedido:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Código do pedido é obrigatório"
            }))
            return
        
        # Extrai nome da impressora, colunas e tipo de impressora (opcionais, vêm do mobile)
        # Aceita tanto "impressora" quanto "nome_impressora" para compatibilidade
        nome_impressora = dados.get("nome_impressora") or dados.get("impressora")
        colunas = dados.get("colunas")
        usa_bematech = dados.get("usa_bematech", None)  # Padrão: None (detecção automática)

        # Valida se a impressora existe (se foi informada)
        if nome_impressora:
            impressoras_disponiveis = listar_impressoras_windows()
            if nome_impressora not in impressoras_disponiveis:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Impressora '{nome_impressora}' não encontrada. Use o comando 'listar_impressoras' para ver as disponíveis."
                }))
                return
        
        # Valida colunas (se informado, deve estar entre 20 e 80)
        if colunas is not None:
            try:
                colunas_int = int(colunas)
                if colunas_int < 20 or colunas_int > 80:
                    await websocket.send(json.dumps({
                        "sucesso": False,
                        "erro": "Número de colunas deve estar entre 20 e 80"
                    }))
                    return
            except (ValueError, TypeError):
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": "Número de colunas inválido"
                }))
                return
        
        # Tenta imprimir
        sucesso = imprimir_venda_por_codigo(cod_pedido, nome_impressora=nome_impressora, colunas=colunas, usa_bematech=usa_bematech)
        
        if sucesso:
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"Cupom do pedido {cod_pedido} impresso com sucesso",
                "impressora_usada": nome_impressora or "padrão",
                "colunas_usadas": colunas or "padrão"
            }))
        else:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Falha ao imprimir o cupom"
            }))
            print(f"❌ Falha ao imprimir cupom do pedido {cod_pedido}")
            
    except Exception as e:
        print(f"❌ Erro ao processar impressão: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def consultar_status_pedidos(websocket, dados):
    """Consulta o status de um ou vários pedidos."""
    try:
        
        # Extrai os códigos de pedido (pode ser um único código ou uma lista)
        codigos_pedido = dados.get("codigos_pedido")
        
        if not codigos_pedido:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Códigos de pedido são obrigatórios"
            }))
            return
        
        # Se for uma string única, converte para lista
        if isinstance(codigos_pedido, str):
            codigos_pedido = [codigos_pedido]
        
        # Valida se é uma lista
        if not isinstance(codigos_pedido, list) or len(codigos_pedido) == 0:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Formato inválido. Envie um código ou uma lista de códigos"
            }))
            return
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Monta a query com placeholders para os códigos
            placeholders = ','.join(['?' for _ in codigos_pedido])
            
            query = f"""
                SELECT 
                    [Código Pedido],
                    CASE
                        WHEN Fechado = 1 AND Parcelado = 1 AND Entregue = 1 THEN 'CONCLUIDO'
                        ELSE 'PENDENTE'
                    END AS Status
                FROM Pedidos
                WHERE [Código Pedido] IN ({placeholders})
            """
            
            cursor.execute(query, codigos_pedido)
            
            # Monta o resultado
            resultados = []
            pedidos_encontrados = set()
            
            for row in cursor.fetchall():
                cod = row[0]
                status = row[1]
                pedidos_encontrados.add(cod)
                resultados.append({
                    "Código Pedido": cod,
                    "Status": status
                })
            
            # Adiciona pedidos não encontrados
            for cod in codigos_pedido:
                if cod not in pedidos_encontrados:
                    resultados.append({
                        "Código Pedido": cod,
                        "Status": "NAO_ENCONTRADO"
                    })
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "pedidos": resultados,
                "total": len(resultados)
            }))
            
            
        finally:
            if conn:
                conn.close()
            
    except Exception as e:
        print(f"❌ Erro ao consultar status de pedidos: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def imprimir_ticket_produto_ws(websocket, dados):
    """Recebe dados de produto(s) e imprime ticket(s) de produto."""
    try:
        
        # Extrai nome da impressora, colunas e tipo de impressora (opcionais)
        nome_impressora = dados.get("nome_impressora") or dados.get("impressora")
        colunas = dados.get("colunas")
        usa_bematech = dados.get("usa_bematech", None)  # Padrão: None (detecção automática)
        
        # Valida se a impressora existe (se foi informada)
        if nome_impressora:
            impressoras_disponiveis = listar_impressoras_windows()
            if nome_impressora not in impressoras_disponiveis:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Impressora '{nome_impressora}' não encontrada. Use o comando 'listar_impressoras' para ver as disponíveis."
                }))
                return
        
        # Valida colunas (se informado, deve estar entre 20 e 80)
        if colunas is not None:
            try:
                colunas_int = int(colunas)
                if colunas_int < 20 or colunas_int > 80:
                    await websocket.send(json.dumps({
                        "sucesso": False,
                        "erro": "Número de colunas deve estar entre 20 e 80"
                    }))
                    return
            except (ValueError, TypeError):
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": "Número de colunas inválido"
                }))
                return
        
        # Extrai vendedor no nível superior (comum a todos os itens)
        cod_vendedor = dados.get("cod_vendedor")
        nome_vendedor = dados.get("nome_vendedor")
        
        # Extrai item ou lista de itens
        item = dados.get("item")
        itens = dados.get("itens", [])
        
        # Se recebeu um único item, converte para lista
        if item and not itens:
            itens = [item]
        elif not item and not itens:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "É necessário enviar 'item' ou 'itens' (lista)"
            }))
            return
        
        # Valida campos obrigatórios de cada item
        # cod_vendedor não é mais obrigatório em cada item se foi informado no nível superior
        campos_obrigatorios_item = ["cod_item", "quantidade", "valor_unitario", "cod_pedido"]
        if not cod_vendedor:
            # Se não informou no nível superior, cada item deve ter cod_vendedor
            campos_obrigatorios_item.append("cod_vendedor")
        
        lista_dados_produto = []
        
        for idx, item_data in enumerate(itens):
            # Valida campos obrigatórios
            campos_faltando = [campo for campo in campos_obrigatorios_item if campo not in item_data]
            if campos_faltando:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Item {idx}: Campos obrigatórios ausentes: {', '.join(campos_faltando)}"
                }))
                return
            
            # Prepara dados do produto
            dados_produto = {
                "cod_item": item_data["cod_item"],
                "descricao": item_data.get("descricao"),  # Opcional, será buscado se não fornecido
                "quantidade": float(item_data["quantidade"]),
                "valor_unitario": float(item_data["valor_unitario"]),
                "cod_pedido": item_data["cod_pedido"],
                "observacao": item_data.get("observacao") or item_data.get("Observacoes")  # Aceita ambos os formatos
            }
            
            lista_dados_produto.append(dados_produto)
        
        # Se cod_vendedor não foi informado no nível superior, usa do primeiro item
        if not cod_vendedor and len(lista_dados_produto) > 0:
            # Tenta pegar do primeiro item (assumindo que todos têm o mesmo vendedor)
            primeiro_item = itens[0] if itens else None
            if primeiro_item:
                cod_vendedor = primeiro_item.get("cod_vendedor")
                nome_vendedor = primeiro_item.get("nome_vendedor")
        
        # Se houver múltiplos itens, usa a função de impressão múltipla
        if len(lista_dados_produto) > 1:
            sucesso = imprimir_tickets_produtos_multiplos(
                lista_dados_produto,
                cod_vendedor=cod_vendedor,
                nome_vendedor=nome_vendedor,
                nome_impressora=nome_impressora,
                colunas=colunas,
                usa_bematech=usa_bematech
            )
        else:
            # Se for apenas um item, usa a função original
            dados_produto = lista_dados_produto[0]
            dados_produto["cod_vendedor"] = cod_vendedor
            dados_produto["nome_vendedor"] = nome_vendedor
            sucesso = imprimir_ticket_produto(
                dados_produto,
                nome_impressora=nome_impressora,
                colunas=colunas,
                usa_bematech=usa_bematech
            )
        
        if sucesso:
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"{len(lista_dados_produto)} ticket(s) impresso(s) com sucesso",
                "total": len(lista_dados_produto),
                "impressora_usada": nome_impressora or "padrão",
                "colunas_usadas": colunas or "padrão"
            }))
        else:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Falha ao imprimir os tickets"
            }))
            
    except Exception as e:
        print(f"❌ Erro ao processar impressão de ticket de produto: {e}")
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def listar_pedidos_mobile(websocket):
    """Lista todos os pedidos mobile pendentes com seus itens."""
    try:
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Busca os pedidos com os filtros especificados
            query_pedidos = """
                SELECT 
                    P.[Código Pedido],
                    P.[Valor Total],
                    P.[Data Emissão],
                    P.[Hora Emissão],
                    P.[Código Vendedor],
                    P.Responsável,
                    P.[Forma Pagamento Mobile],
                    P.[Código Cliente]
                FROM Pedidos P
                WHERE P.[Origem Venda] = '3 - Mobile'
                  AND P.Fechado = 0
                  AND P.Entregue = 0
                  AND P.Parcelado = 0
                ORDER BY P.[Data Emissão] DESC, P.[Código Pedido] DESC
            """
            
            cursor.execute(query_pedidos)
            pedidos_rows = cursor.fetchall()
            
            # Busca o código do cliente padrão para comparação
            cod_cliente_padrao = None
            try:
                cursor.execute("SELECT [Código Cliente à Vista] FROM opções")
                row_padrao = cursor.fetchone()
                if row_padrao and row_padrao[0]:
                    cod_cliente_padrao = row_padrao[0]
            except Exception:
                pass  # Se não conseguir buscar, continua sem comparar
            
            # Monta a lista de pedidos
            pedidos = []
            
            for row in pedidos_rows:
                cod_pedido = row[0]
                valor_total = float(row[1]) if row[1] else 0.0
                data_emissao = row[2] if row[2] else None
                hora_emissao = row[3] if row[3] else None
                cod_vendedor = row[4] if row[4] else None
                responsavel = row[5] if row[5] else None
                forma_pagamento_mobile = row[6] if row[6] else None
                cod_cliente = row[7] if row[7] else None
                
                # Formata data e hora
                data_hora_str = None
                if data_emissao:
                    data_str = data_emissao.strftime("%Y-%m-%d")
                    if hora_emissao:
                        hora_str = hora_emissao.strftime("%H:%M:%S")
                        data_hora_str = f"{data_str} {hora_str}"
                    else:
                        data_hora_str = data_str
                
                # Busca o nome do vendedor se tiver código
                nome_vendedor = None
                if cod_vendedor:
                    cursor.execute("""
                        SELECT [Nome Funcionário]
                        FROM Funcionários
                        WHERE [Código Funcionário] = ?
                    """, cod_vendedor)
                    vendedor_row = cursor.fetchone()
                    if vendedor_row and vendedor_row[0]:
                        nome_vendedor = vendedor_row[0]
                
                # Busca o nome do cliente se tiver código e não for cliente padrão
                nome_cliente = None
                if cod_cliente and cod_cliente != cod_cliente_padrao:
                    cursor.execute("""
                        SELECT [Nome Cliente]
                        FROM Clientes
                        WHERE [Código Cliente] = ?
                    """, cod_cliente)
                    cliente_row = cursor.fetchone()
                    if cliente_row and cliente_row[0]:
                        nome_cliente = cliente_row[0]
                # Se for cliente padrão, nome_cliente permanece None (null)
                
                # Busca os itens do pedido
                query_itens = """
                    SELECT 
                        PI.SEQ,
                        PI.[Código Item],
                        PI.Quantidade,
                        PI.[Valor Unitário],
                        PI.[Valor Total],
                        PI.Observações,
                        E.[Descrição Item]
                    FROM [Pedidos Itens] PI
                    LEFT JOIN Estoque E ON PI.[Código Item] = E.[Código Item]
                    WHERE PI.[Código Pedido] = ?
                    ORDER BY PI.SEQ
                """
                
                cursor.execute(query_itens, cod_pedido)
                itens_rows = cursor.fetchall()
                
                # Monta a lista de itens
                itens = []
                for item_row in itens_rows:
                    itens.append({
                        "seq": item_row[0] if item_row[0] else None,
                        "cod_item": item_row[1] if item_row[1] else None,
                        "quantidade": float(item_row[2]) if item_row[2] else 0.0,
                        "valor_unitario": float(item_row[3]) if item_row[3] else 0.0,
                        "valor_total": float(item_row[4]) if item_row[4] else 0.0,
                        "observacoes": item_row[5] if item_row[5] else None,
                        "descricao_item": item_row[6] if item_row[6] else None
                    })
                
                # Adiciona o pedido com seus itens
                pedidos.append({
                    "cod_pedido": cod_pedido,
                    "total": valor_total,
                    "data": data_hora_str,
                    "cod_vendedor": cod_vendedor,
                    "nome_vendedor": nome_vendedor,
                    "cod_cliente": cod_cliente,
                    "nome_cliente": nome_cliente,
                    "responsavel": responsavel,
                    "forma_pagamento_mobile": forma_pagamento_mobile,
                    "itens": itens
                })
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "pedidos": pedidos,
                "total": len(pedidos)
            }))
            
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"❌ Erro ao listar pedidos mobile: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

async def alterar_pedido(websocket, dados):
    """Altera dados de um pedido existente (cliente, responsável, forma de pagamento)."""
    try:
        # Extrai código do pedido (obrigatório)
        cod_pedido = dados.get("cod_pedido")
        if not cod_pedido:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Código do pedido é obrigatório"
            }))
            return
        
        # Extrai campos opcionais para alteração
        cod_cliente = dados.get("cod_cliente")
        responsavel = dados.get("responsavel")
        forma_pagamento_mobile = dados.get("forma_pagamento_mobile")
        
        # Valida se pelo menos um campo foi informado
        if cod_cliente is None and responsavel is None and forma_pagamento_mobile is None:
            await websocket.send(json.dumps({
                "sucesso": False,
                "erro": "Informe pelo menos um campo para alterar: cod_cliente, responsavel ou forma_pagamento_mobile"
            }))
            return
        
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        try:
            # Verifica se o pedido existe
            cursor.execute("""
                SELECT [Código Pedido], Fechado, Entregue, Parcelado
                FROM Pedidos
                WHERE [Código Pedido] = ?
            """, cod_pedido)
            
            pedido_row = cursor.fetchone()
            if not pedido_row:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Pedido {cod_pedido} não encontrado"
                }))
                return
            
            # Verifica se o pedido pode ser alterado (não pode estar fechado, entregue ou parcelado)
            if pedido_row[1] == 1 or pedido_row[2] == 1 or pedido_row[3] == 1:
                await websocket.send(json.dumps({
                    "sucesso": False,
                    "erro": f"Pedido {cod_pedido} não pode ser alterado (já está fechado, entregue ou parcelado)"
                }))
                return
            
            # Monta a query de UPDATE dinamicamente com apenas os campos informados
            campos_update = []
            valores_update = []
            
            if cod_cliente is not None:
                campos_update.append("[Código Cliente] = ?")
                valores_update.append(cod_cliente)
            
            if responsavel is not None:
                campos_update.append("Responsável = ?")
                valores_update.append(responsavel if responsavel.strip() else None)
            
            if forma_pagamento_mobile is not None:
                campos_update.append("[Forma Pagamento Mobile] = ?")
                valores_update.append(forma_pagamento_mobile if forma_pagamento_mobile.strip() else None)
            
            # Sempre atualiza data de atualização e quem atualizou
            campos_update.append("[Data Atualização] = ?")
            valores_update.append(datetime.now())
            campos_update.append("Atualizado = ?")
            valores_update.append('MOBILE')
            
            # Adiciona o código do pedido no WHERE
            valores_update.append(cod_pedido)
            
            # Monta e executa a query
            sql = f"""
                UPDATE Pedidos
                SET {', '.join(campos_update)}
                WHERE [Código Pedido] = ?
            """
            
            cursor.execute(sql, valores_update)
            conn.commit()
            
            await websocket.send(json.dumps({
                "sucesso": True,
                "mensagem": f"Pedido {cod_pedido} alterado com sucesso",
                "cod_pedido": cod_pedido,
                "campos_alterados": {
                    "cod_cliente": cod_cliente if cod_cliente is not None else None,
                    "responsavel": responsavel if responsavel is not None else None,
                    "forma_pagamento_mobile": forma_pagamento_mobile if forma_pagamento_mobile is not None else None
                }
            }))
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"❌ Erro ao alterar pedido: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send(json.dumps({
            "sucesso": False,
            "erro": str(e)
        }))

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
