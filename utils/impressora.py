# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de impressão térmica em impressoras Windows
Suporta impressoras de 80mm (42 colunas por padrão)
"""

import win32print
import win32ui
import win32con
from datetime import datetime
from utils.sqlserver import conexao_ativa
from utils.config import criar_settings


def listar_impressoras_windows():
    """Retorna uma lista com todas as impressoras instaladas no Windows."""
    try:
        impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        return impressoras
    except Exception as e:
        print(f"❌ Erro ao listar impressoras: {e}")
        return []


def obter_impressora_padrao():
    """Retorna o nome da impressora padrão configurada no sistema."""
    try:
        return win32print.GetDefaultPrinter()
    except Exception as e:
        print(f"❌ Erro ao obter impressora padrão: {e}")
        return None


def obter_impressora_configurada():
    """Retorna a impressora configurada no config.json ou a padrão do sistema."""
    settings = criar_settings()
    impressora = settings.value("impressora", "")
    
    if impressora and impressora in listar_impressoras_windows():
        return impressora
    else:
        return obter_impressora_padrao()


def obter_colunas_configuradas():
    """Retorna o número de colunas configurado no config.json."""
    settings = criar_settings()
    colunas_str = settings.value("colunas_impressora", "42")
    
    try:
        colunas = int(colunas_str)
        # Valida o range (entre 20 e 80)
        if colunas < 20 or colunas > 80:
            return 42  # Retorna padrão se estiver fora do range
        return colunas
    except (ValueError, TypeError):
        return 42  # Retorna padrão em caso de erro


def obter_nome_empresa():
    """Busca o nome da empresa no banco de dados."""
    try:
        conn = conexao_ativa()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP(1) [Nome Empresa] FROM Empresas")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return row[0]
        else:
            return "EMPRESA"
    except Exception as e:
        print(f"⚠️ Erro ao buscar nome da empresa: {e}")
        return "EMPRESA"


class ImpressoraTermica:
    """Classe para gerenciar impressão em impressoras térmicas."""
    
    def __init__(self, impressora=None, width_cols=None, usa_bematech=None):
        """
        Inicializa a impressora térmica usando GDI do Windows.
        
        Args:
            impressora (str): Nome da impressora. Se None, usa a configurada.
            width_cols (int): Largura em colunas. Se None, usa o valor configurado.
            usa_bematech (bool, optional): Parâmetro mantido por compatibilidade, mas não afeta o comportamento.
                                          A impressão sempre usa GDI, independente da marca.
        """
        self.impressora = impressora or obter_impressora_configurada()
        self.width_cols = width_cols if width_cols is not None else obter_colunas_configuradas()
        self.linhas = []
        
        if not self.impressora:
            raise Exception("Nenhuma impressora disponível")
        
        # Log do tipo de impressora (apenas informativo, não afeta comportamento)
        if usa_bematech is not None:
            tipo_impressora = "Bematech" if usa_bematech else "Elgin"
    
    def adicionar_linha(self, texto="", centralizar=False, negrito=False, tamanho_grande=False, tamanho_medio=False):
        """Adiciona uma linha ao buffer de impressão."""
        if centralizar:
            espacos = (self.width_cols - len(texto)) // 2
            texto = " " * espacos + texto
        
        # Não trunca - deixa a função de desenho fazer a quebra por pixels
        # Isso garante que textos longos sejam quebrados corretamente sem corte
        
        self.linhas.append({
            "texto": texto,
            "negrito": negrito,
            "tamanho_grande": tamanho_grande,
            "tamanho_medio": tamanho_medio
        })
    
    def adicionar_separador(self, caractere="-"):
        """Adiciona uma linha separadora."""
        self.adicionar_linha(caractere * self.width_cols)
    
    def adicionar_linha_dupla(self, esquerda, direita, preencher=" "):
        """Adiciona uma linha com texto à esquerda e à direita."""
        espaco_disponivel = self.width_cols - len(esquerda) - len(direita)
        if espaco_disponivel < 0:
            # Trunca textos se não couber
            esquerda = esquerda[:self.width_cols // 2]
            direita = direita[:self.width_cols // 2]
            espaco_disponivel = self.width_cols - len(esquerda) - len(direita)
        
        linha = esquerda + (preencher * espaco_disponivel) + direita
        self.adicionar_linha(linha)
    
    def limpar_buffer(self):
        """Limpa o buffer de linhas."""
        self.linhas = []
    
    def imprimir_cupom_venda(self, dados_venda):
        """
        Imprime um cupom de venda/orçamento/condicional.
        
        Args:
            dados_venda (dict): Dicionário com os dados da venda:
                - cod_pedido: Código do pedido
                - documento_venda: Tipo de documento (1-Pedido, 2-Orçamento, 3-Condicional)
                - nome_cliente: Nome do cliente
                - endereco_cliente: Endereço completo do cliente (opcional)
                - nome_vendedor: Nome do vendedor
                - responsavel: Nome do responsável (opcional)
                - forma_pagamento: Forma de pagamento (opcional)
                - data_emissao: Data da emissão
                - hora_emissao: Hora da emissão
                - itens: Lista de itens [{"descricao", "quantidade", "valor_unitario", "valor_total"}]
                - quantidade_total: Quantidade total de itens
                - valor_total: Valor total da venda
        """
        self.limpar_buffer()
        
        # Determina o tipo de documento
        documento_venda = dados_venda.get('documento_venda', '1 - Pedido')
        
        # Define o título do cupom e o label do código baseado no tipo de documento
        if '2' in str(documento_venda) or 'Orcamento' in str(documento_venda) or 'ORCAMENTO' in str(documento_venda):
            titulo_cupom = "CUPOM DE ORCAMENTO"
            label_codigo = "Orcamento"
        elif '3' in str(documento_venda) or 'Condicional' in str(documento_venda) or 'CONDICIONAL' in str(documento_venda):
            titulo_cupom = "CUPOM CONDICIONAL"
            label_codigo = "Condicional"
        else:
            titulo_cupom = "CUPOM DE VENDA"
            label_codigo = "Pedido"
        
        # Cabeçalho - Nome da Empresa
        nome_empresa = obter_nome_empresa()
        self.adicionar_linha()
        self.adicionar_linha(nome_empresa, centralizar=True, negrito=True, tamanho_grande=True)
        self.adicionar_linha()
        self.adicionar_separador("=")
        self.adicionar_linha(titulo_cupom, centralizar=True, negrito=True)
        self.adicionar_separador("=")
        self.adicionar_linha()
        
        # Informações do pedido/orçamento/condicional
        self.adicionar_linha(f"{label_codigo}: {dados_venda['cod_pedido']}")
        self.adicionar_linha(f"Data: {dados_venda['data_emissao']} {dados_venda['hora_emissao']}")
        self.adicionar_linha()
        
        # Cliente e Endereço
        self.adicionar_linha(f"Cliente: {dados_venda['nome_cliente'][:self.width_cols-9]}")
        
        # Endereço do cliente (se existir)
        if dados_venda.get('endereco_cliente'):
            # Processa endereço que pode ter \n
            linhas_endereco = dados_venda['endereco_cliente'].split('\n')
            for linha_end in linhas_endereco:
                if linha_end.strip():
                    # Quebra em múltiplas linhas se necessário
                    if len(linha_end) > self.width_cols:
                        for i in range(0, len(linha_end), self.width_cols):
                            self.adicionar_linha(linha_end[i:i+self.width_cols])
                    else:
                        self.adicionar_linha(linha_end[:self.width_cols])
        
        self.adicionar_linha()
        
        # Vendedor
        self.adicionar_linha(f"Vendedor: {dados_venda['nome_vendedor'][:self.width_cols-10]}")
        
        # Responsável (se existir e for diferente do vendedor)
        if dados_venda.get('responsavel') and dados_venda['responsavel'].strip():
            self.adicionar_linha(f"Resp.: {dados_venda['responsavel'][:self.width_cols-7]}")
        
        # Forma de Pagamento
        if dados_venda.get('forma_pagamento'):
            self.adicionar_linha(f"Pgto: {dados_venda['forma_pagamento'][:self.width_cols-6]}")
        
        self.adicionar_linha()
        self.adicionar_separador("-")
        
        # Cabeçalho dos itens
        self.adicionar_linha("ITEM                      QTD  TOTAL")
        self.adicionar_separador("-")
        
        # Itens
        for item in dados_venda['itens']:
            descricao = item['descricao']
            quantidade = f"{item['quantidade']:.2f}"
            valor_total = f"{item['valor_total']:.2f}"
            
            # Descrição completa com quebra por colunas
            # Quebra a descrição em múltiplas linhas baseado no número de colunas
            palavras = descricao.split()
            linha_atual = ""
            for palavra in palavras:
                # Testa se a palavra cabe na linha atual
                teste_linha = (linha_atual + " " + palavra).strip() if linha_atual else palavra
                # Se exceder o limite de colunas, pula para próxima linha
                if len(teste_linha) > self.width_cols:
                    if linha_atual:
                        self.adicionar_linha(linha_atual)
                    linha_atual = palavra
                    # Se a palavra sozinha for maior que a largura, quebra ela também
                    if len(palavra) > self.width_cols:
                        # Quebra palavra muito longa em pedaços
                        for i in range(0, len(palavra), self.width_cols):
                            self.adicionar_linha(palavra[i:i+self.width_cols])
                        linha_atual = ""
                else:
                    linha_atual = teste_linha
            # Adiciona a última linha se houver
            if linha_atual:
                self.adicionar_linha(linha_atual)
            
            # Linha seguinte: Valor unitário, quantidade e total
            valor_unit_str = f"R$ {item['valor_unitario']:.2f}"
            qtd_str = f"x{quantidade}"
            total_str = f"R$ {valor_total}"
            
            # Calcula espaçamento
            espacos = self.width_cols - len(valor_unit_str) - len(qtd_str) - len(total_str) - 2
            linha_valores = f" {valor_unit_str} {qtd_str}" + (" " * espacos) + total_str
            self.adicionar_linha(linha_valores)
            self.adicionar_linha()
        
        # Separador antes do total
        self.adicionar_separador("-")
        
        # Quantidade total de itens
        qtd_total_str = f"Qtd. Total: {dados_venda['quantidade_total']:.2f}"
        self.adicionar_linha(qtd_total_str)
        
        # Valor total
        self.adicionar_separador("=")
        valor_total_str = f"R$ {dados_venda['valor_total']:.2f}"
        self.adicionar_linha_dupla("TOTAL:", valor_total_str, " ")
        self.adicionar_separador("=")
        
        # Rodapé
        self.adicionar_linha()
        self.adicionar_linha("Obrigado pela preferencia!", centralizar=True)
        self.adicionar_linha()
        self.adicionar_linha()
        self.adicionar_linha("Desenvolvido por", centralizar=True)
        self.adicionar_linha("WM Sistemas de Gestao", centralizar=True)
        self.adicionar_linha()
        self.adicionar_linha()
        
        # Envia para impressão
        return self._enviar_para_impressora()
    
    def _enviar_para_impressora(self):
        """Envia o buffer de linhas para a impressora usando GDI do Windows."""
        printer_dc = None
        old_font = None

        try:
            # Cria um Device Context para a impressora
            printer_dc = win32ui.CreateDC()
            printer_dc.CreatePrinterDC(self.impressora)

            # Pega o DPI vertical da impressora para calcular altura real em pontos
            dpi_y = printer_dc.GetDeviceCaps(win32con.LOGPIXELSY)

            def altura_em_pontos(pt):
                """
                Converte tamanho em pontos (pt) para altura lógica negativa,
                conforme padrão do CreateFont (pt * dpi / 72).
                """
                return -int(pt * dpi_y / 72)

            # 🔹 Tamanhos em pontos (ajustados: um pouco menores)
            pt_normal = 11      # corpo do texto
            pt_medio = 13       # tamanho intermediário (para descrição de produtos)
            pt_grande = 16      # títulos / destaque

            altura_normal = altura_em_pontos(pt_normal)
            altura_medio = altura_em_pontos(pt_medio)
            altura_grande = altura_em_pontos(pt_grande)

            # Fonte monoespaçada (mais previsível em impressora)
            fonte_nome = "Lucida Console"  # pode trocar por "Consolas" se preferir

            # Cria fontes diferentes para cada estilo
            font_normal = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_normal,
                "weight": win32con.FW_NORMAL,
                "charset": win32con.DEFAULT_CHARSET,
            })

            font_negrito = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_normal,
                "weight": win32con.FW_BOLD,
                "charset": win32con.DEFAULT_CHARSET,
            })

            font_medio = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_medio,
                "weight": win32con.FW_NORMAL,
                "charset": win32con.DEFAULT_CHARSET,
            })

            font_medio_negrito = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_medio,
                "weight": win32con.FW_BOLD,
                "charset": win32con.DEFAULT_CHARSET,
            })

            font_grande = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_grande,
                "weight": win32con.FW_NORMAL,
                "charset": win32con.DEFAULT_CHARSET,
            })

            font_grande_negrito = win32ui.CreateFont({
                "name": fonte_nome,
                "height": altura_grande,
                "weight": win32con.FW_BOLD,
                "charset": win32con.DEFAULT_CHARSET,
            })

            # Seleciona a fonte normal inicial
            old_font = printer_dc.SelectObject(font_normal)

            # Calcula altura da linha usando a fonte normal
            (_, text_height) = printer_dc.GetTextExtent("Ag")
            line_height = text_height + 4  # pequeno espaçamento extra

            # Descobre largura máxima em pixels com base em width_cols
            # Como a fonte é monoespaçada, usamos a largura de um caractere * número de colunas
            (char_width, _) = printer_dc.GetTextExtent("A")
            max_width_px = self.width_cols * char_width

            # Margens e posição inicial (pode ajustar se quiser mais pra esquerda/direita)
            x_inicial = 20   # margem esquerda
            y_atual = 20     # margem superior

            # Função auxiliar para desenhar um texto com quebra de linha
            def desenhar_texto_quebrado(texto, fonte, line_height_base):
                nonlocal y_atual

                printer_dc.SelectObject(fonte)

                # Recalcula altura da linha baseada na fonte atual
                (_, h) = printer_dc.GetTextExtent("Ag")
                line_h = h + 4 if line_height_base is None else line_height_base

                # Para fonte grande, reduz a largura máxima em ~25% para evitar corte
                # Calcula largura de um caractere com a fonte atual
                (char_w_atual, _) = printer_dc.GetTextExtent("A")
                # Ajusta largura máxima considerando que fonte grande precisa de mais espaço
                # Se a fonte atual for maior que a normal, reduz a largura disponível
                largura_max_ajustada = max_width_px
                if char_w_atual > char_width * 1.2:  # Se fonte for ~20% maior que normal
                    largura_max_ajustada = int(max_width_px * 0.85)  # Reduz 15% da largura

                # Garante string
                if not isinstance(texto, str):
                    texto_local = str(texto)
                else:
                    texto_local = texto

                # Se for vazio, só pula uma linha
                if not texto_local:
                    y_atual += line_h
                    return

                palavras = texto_local.split(" ")
                linha_atual = ""

                for palavra in palavras:
                    teste = (linha_atual + " " + palavra).strip()
                    (w, _) = printer_dc.GetTextExtent(teste)

                    if w <= largura_max_ajustada:
                        linha_atual = teste
                    else:
                        # Desenha a linha atual e começa outra
                        if linha_atual:
                            printer_dc.TextOut(x_inicial, y_atual, linha_atual)
                            y_atual += line_h
                        linha_atual = palavra

                # Desenha última linha restante
                if linha_atual:
                    printer_dc.TextOut(x_inicial, y_atual, linha_atual)
                    y_atual += line_h

            # Inicia documento e página
            printer_dc.StartDoc("Cupom de Venda")
            printer_dc.StartPage()

            # Desenha cada linha com formatação e quebra automática
            for linha_info in self.linhas:
                texto = linha_info["texto"]

                # Seleciona a fonte apropriada baseada nos atributos da linha
                if linha_info.get("tamanho_grande", False) and linha_info.get("negrito", False):
                    fonte_atual = font_grande_negrito
                    line_height_atual = None  # será recalculado pela função
                elif linha_info.get("tamanho_grande", False):
                    fonte_atual = font_grande
                    line_height_atual = None
                elif linha_info.get("tamanho_medio", False) and linha_info.get("negrito", False):
                    fonte_atual = font_medio_negrito
                    line_height_atual = None  # será recalculado pela função
                elif linha_info.get("tamanho_medio", False):
                    fonte_atual = font_medio
                    line_height_atual = None
                elif linha_info.get("negrito", False):
                    fonte_atual = font_negrito
                    line_height_atual = line_height
                else:
                    fonte_atual = font_normal
                    line_height_atual = line_height

                desenhar_texto_quebrado(texto, fonte_atual, line_height_atual)

            # Linhas em branco no final
            y_atual += 3 * line_height

            # Finaliza página e documento
            printer_dc.EndPage()
            printer_dc.EndDoc()

            # Restaura fonte antiga
            if old_font:
                printer_dc.SelectObject(old_font)

            return True

        except Exception as e:
            print(f"❌ Erro ao imprimir via GDI: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if printer_dc:
                try:
                    if old_font:
                        printer_dc.SelectObject(old_font)
                    printer_dc.DeleteDC()
                except:
                    pass


def imprimir_venda_por_codigo(cod_pedido, nome_impressora=None, colunas=None, usa_bematech=None):
    """
    Busca os dados de uma venda pelo código do pedido e imprime.
    
    Args:
        cod_pedido (str): Código do pedido
        nome_impressora (str, optional): Nome da impressora a usar. Se None, usa a configurada.
        colunas (int, optional): Número de colunas. Se None, usa o valor configurado.
        usa_bematech (bool, optional): Parâmetro mantido por compatibilidade, mas não afeta o comportamento.
                                        A impressão sempre usa GDI, independente da marca. Padrão: None
        
    Returns:
        bool: True se imprimiu com sucesso, False caso contrário
    """
    try:
        conn = conexao_ativa()
        cursor = conn.cursor()
        
        # Busca dados do pedido com forma de pagamento, responsável e endereço do cliente
        cursor.execute("""
            SELECT 
                P.[Código Pedido],
                C.[Nome Cliente],
                F.[Nome Funcionário] as [Nome Vendedor],
                CONVERT(varchar, P.[Data Emissão], 103) as [Data Emissão],
                CONVERT(varchar, P.[Hora Emissão], 108) as [Hora Emissão],
                P.[Valor Total],
                P.[Quantidade Produtos],
                ISNULL(P.[Forma Pagamento Mobile], 'Nao informado') as [Forma Pagamento],
                P.Responsável,
                C.Endereço,
                C.Número,
                C.Bairro,
                C.Cidade,
                C.Estado,
                C.CEP,
                P.[Documento Venda]
            FROM Pedidos P
            LEFT JOIN Clientes C ON P.[Código Cliente] = C.[Código Cliente]
            LEFT JOIN Funcionários F ON P.[Código Vendedor] = F.[Código Funcionário]
            WHERE P.[Código Pedido] = ?
        """, cod_pedido)
        
        pedido_row = cursor.fetchone()
        
        if not pedido_row:
            print(f"❌ Pedido {cod_pedido} não encontrado")
            conn.close()
            return False
        
        # Busca itens do pedido
        cursor.execute("""
            SELECT 
                E.[Descrição Item],
                PI.Quantidade,
                PI.[Valor Unitário],
                PI.[Valor Total]
            FROM [Pedidos Itens] PI
            LEFT JOIN Estoque E ON PI.[Código Item] = E.[Código Item]
            WHERE PI.[Código Pedido] = ?
            ORDER BY PI.SEQ
        """, cod_pedido)
        
        itens_rows = cursor.fetchall()
        conn.close()
        
        # Monta o endereço completo do cliente
        endereco_completo = ""
        if pedido_row[9]:  # Endereço
            endereco_partes = []
            if pedido_row[9]:  # Endereço
                endereco_partes.append(pedido_row[9])
            if pedido_row[10]:  # Número
                endereco_partes.append(f"N {pedido_row[10]}")
            endereco_linha1 = ", ".join(endereco_partes) if endereco_partes else ""
            
            endereco_partes2 = []
            if pedido_row[11]:  # Bairro
                endereco_partes2.append(pedido_row[11])
            if pedido_row[12] and pedido_row[13]:  # Cidade e Estado
                endereco_partes2.append(f"{pedido_row[12]}/{pedido_row[13]}")
            endereco_linha2 = " - ".join(endereco_partes2) if endereco_partes2 else ""
            
            if pedido_row[14]:  # CEP
                endereco_linha2 += f" - CEP: {pedido_row[14]}" if endereco_linha2 else f"CEP: {pedido_row[14]}"
            
            endereco_completo = f"{endereco_linha1}\n{endereco_linha2}" if endereco_linha1 and endereco_linha2 else (endereco_linha1 or endereco_linha2)
        
        # Monta o dicionário de dados
        dados_venda = {
            "cod_pedido": pedido_row[0],
            "nome_cliente": pedido_row[1] or "CONSUMIDOR",
            "nome_vendedor": pedido_row[2] or "VENDEDOR",
            "data_emissao": pedido_row[3] or datetime.now().strftime("%d/%m/%Y"),
            "hora_emissao": pedido_row[4] or datetime.now().strftime("%H:%M:%S"),
            "valor_total": float(pedido_row[5] or 0),
            "quantidade_total": float(pedido_row[6] or 0),
            "forma_pagamento": pedido_row[7] or "Nao informado",
            "responsavel": pedido_row[8] or "",
            "endereco_cliente": endereco_completo,
            "documento_venda": pedido_row[15] or "1 - Pedido",
            "itens": []
        }
        
        for item_row in itens_rows:
            dados_venda["itens"].append({
                "descricao": item_row[0] or "PRODUTO",
                "quantidade": float(item_row[1] or 0),
                "valor_unitario": float(item_row[2] or 0),
                "valor_total": float(item_row[3] or 0)
            })
        
        # Imprime
        # Se nome_impressora ou colunas foram fornecidos, usa-os; senão usa os configurados
        if nome_impressora or colunas is not None:
            # Converte colunas para int se fornecido
            colunas_int = int(colunas) if colunas is not None else None
            impressora = ImpressoraTermica(impressora=nome_impressora, width_cols=colunas_int, usa_bematech=usa_bematech)
        else:
            # Usa configuração padrão
            impressora = ImpressoraTermica(usa_bematech=usa_bematech)
        
        return impressora.imprimir_cupom_venda(dados_venda)
        
    except Exception as e:
        print(f"❌ Erro ao imprimir venda: {e}")
        return False


def imprimir_tickets_produtos_multiplos(lista_dados_produto, cod_vendedor=None, nome_vendedor=None, nome_impressora=None, colunas=None, usa_bematech=None):
    """
    Imprime múltiplos tickets de produto em um único documento, com separadores entre eles.
    Vendedor e hora são mostrados apenas no final.
    
    Args:
        lista_dados_produto (list): Lista de dicionários com dados dos produtos
        cod_vendedor (str, optional): Código do vendedor (comum a todos os tickets)
        nome_vendedor (str, optional): Nome do vendedor (comum a todos os tickets)
        nome_impressora (str, optional): Nome da impressora a usar
        colunas (int, optional): Número de colunas
        usa_bematech (bool, optional): Parâmetro mantido por compatibilidade
        
    Returns:
        bool: True se imprimiu com sucesso, False caso contrário
    """
    try:
        # Busca nome do vendedor se não foi fornecido mas cod_vendedor foi
        if not nome_vendedor and cod_vendedor:
            conn = conexao_ativa()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT [Nome Funcionário]
                FROM Funcionários
                WHERE [Código Funcionário] = ?
            """, cod_vendedor)
            row = cursor.fetchone()
            if row and row[0]:
                nome_vendedor = row[0]
            else:
                nome_vendedor = "VENDEDOR"
            conn.close()
        
        # Inicializa impressora
        if nome_impressora or colunas is not None:
            colunas_int = int(colunas) if colunas is not None else None
            impressora = ImpressoraTermica(impressora=nome_impressora, width_cols=colunas_int, usa_bematech=usa_bematech)
        else:
            impressora = ImpressoraTermica(usa_bematech=usa_bematech)
        
        # Limpa buffer
        impressora.limpar_buffer()
        
        # Cabeçalho - Nome da Empresa (tamanho normal) - apenas uma vez no início
        nome_empresa = obter_nome_empresa()
        impressora.adicionar_linha()
        impressora.adicionar_linha(nome_empresa, centralizar=True, negrito=True)
        impressora.adicionar_linha()
        impressora.adicionar_separador("=")
        impressora.adicionar_linha()
        
        # Processa cada produto
        for idx, dados_produto in enumerate(lista_dados_produto):
            # Busca descrição do produto se não foi fornecida
            if not dados_produto.get('descricao'):
                conn = conexao_ativa()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT [Descrição Item]
                    FROM Estoque
                    WHERE [Código Item] = ?
                """, dados_produto['cod_item'])
                row = cursor.fetchone()
                if row and row[0]:
                    dados_produto['descricao'] = row[0]
                else:
                    dados_produto['descricao'] = "PRODUTO"
                conn.close()
            
            # Se não for o primeiro item, adiciona separador
            if idx > 0:
                impressora.adicionar_linha()
                impressora.adicionar_separador("-")
                impressora.adicionar_linha()
            
            # Busca responsável e cliente do pedido (se tiver cod_pedido)
            nome_cliente_info = None
            if dados_produto.get('cod_pedido'):
                try:
                    conn = conexao_ativa()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT 
                            P.Responsável,
                            C.[Nome Cliente]
                        FROM Pedidos P
                        LEFT JOIN Clientes C ON P.[Código Cliente] = C.[Código Cliente]
                        WHERE P.[Código Pedido] = ?
                    """, dados_produto['cod_pedido'])
                    row = cursor.fetchone()
                    if row:
                        responsavel = row[0] if row[0] else None
                        nome_cliente = row[1] if row[1] else None
                        # Prioridade: responsável primeiro, depois cliente
                        if responsavel and responsavel.strip():
                            nome_cliente_info = responsavel.strip()
                        elif nome_cliente and nome_cliente.strip():
                            nome_cliente_info = nome_cliente.strip()
                    conn.close()
                except Exception as e:
                    pass  # Ignora erro silenciosamente
            
            # Exibe código do pedido e cliente/responsável se tiver (apenas no primeiro item)
            if idx == 0:
                if dados_produto.get('cod_pedido'):
                    impressora.adicionar_linha(f"Pedido: {dados_produto['cod_pedido']}")
                if nome_cliente_info:
                    impressora.adicionar_linha(f"Cliente: {nome_cliente_info[:impressora.width_cols-9]}")
                if dados_produto.get('cod_pedido') or nome_cliente_info:
                    impressora.adicionar_linha()
            
            # Quantidade (em destaque)
            quantidade = dados_produto.get('quantidade', 0)
            impressora.adicionar_linha(f"QUANTIDADE: {quantidade:.2f}", negrito=True)
            impressora.adicionar_linha()
            
            # Descrição do produto (em tamanho médio, negrito) - quebra automática por pixels
            descricao = dados_produto.get('descricao', 'PRODUTO')
            # Usa tamanho_medio para que a função de desenho faça a quebra inteligente por pixels
            impressora.adicionar_linha(descricao, negrito=True, tamanho_medio=True)
            
            impressora.adicionar_linha()
            
            # Observação (se houver)
            observacao = dados_produto.get('observacao')
            if observacao and observacao.strip():
                # Quebra observação em múltiplas linhas se necessário
                palavras_obs = observacao.split()
                linha_atual = ""
                for palavra in palavras_obs:
                    if len(linha_atual + " " + palavra) <= impressora.width_cols:
                        linha_atual += (" " if linha_atual else "") + palavra
                    else:
                        if linha_atual:
                            impressora.adicionar_linha(linha_atual)
                        linha_atual = palavra
                if linha_atual:
                    impressora.adicionar_linha(linha_atual)
                impressora.adicionar_linha()
        
        # No final, mostra vendedor e hora (apenas uma vez)
        impressora.adicionar_linha()
        impressora.adicionar_separador("=")
        impressora.adicionar_linha()
        
        # Hora de impressão
        hora_impressao = datetime.now().strftime("%H:%M:%S")
        impressora.adicionar_linha(f"Hora: {hora_impressao}")
        
        # Vendedor
        if nome_vendedor:
            impressora.adicionar_linha(f"Vendedor: {nome_vendedor[:impressora.width_cols-10]}")
        
        # Rodapé
        impressora.adicionar_linha()
        impressora.adicionar_linha()
        
        # Envia para impressão
        return impressora._enviar_para_impressora()
        
    except Exception as e:
        print(f"❌ Erro ao imprimir tickets de produto: {e}")
        import traceback
        traceback.print_exc()
        return False


def imprimir_ticket_produto(dados_produto, nome_impressora=None, colunas=None, usa_bematech=None):
    """
    Imprime um ticket de produto individual.
    
    Args:
        dados_produto (dict): Dicionário com os dados do produto:
            - cod_item: Código do item
            - descricao: Descrição do produto
            - quantidade: Quantidade
            - valor_unitario: Valor unitário
            - cod_vendedor: Código do vendedor
            - nome_vendedor: Nome do vendedor (opcional, será buscado se não fornecido)
            - cod_pedido: Código do pedido
            - observacao: Observação do item (opcional)
        nome_impressora (str, optional): Nome da impressora a usar. Se None, usa a configurada.
        colunas (int, optional): Número de colunas. Se None, usa o valor configurado.
        usa_bematech (bool, optional): Parâmetro mantido por compatibilidade, mas não afeta o comportamento.
                                        A impressão sempre usa GDI, independente da marca. Padrão: None
        
    Returns:
        bool: True se imprimiu com sucesso, False caso contrário
    """
    try:
        # Busca descrição do produto se não foi fornecida
        if not dados_produto.get('descricao'):
            conn = conexao_ativa()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT [Descrição Item]
                FROM Estoque
                WHERE [Código Item] = ?
            """, dados_produto['cod_item'])
            row = cursor.fetchone()
            if row and row[0]:
                dados_produto['descricao'] = row[0]
            else:
                dados_produto['descricao'] = "PRODUTO"
            conn.close()
        
        # Busca nome do vendedor se não foi fornecido
        if not dados_produto.get('nome_vendedor') and dados_produto.get('cod_vendedor'):
            conn = conexao_ativa()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT [Nome Funcionário]
                FROM Funcionários
                WHERE [Código Funcionário] = ?
            """, dados_produto['cod_vendedor'])
            row = cursor.fetchone()
            if row and row[0]:
                dados_produto['nome_vendedor'] = row[0]
            else:
                dados_produto['nome_vendedor'] = "VENDEDOR"
            conn.close()
        
        # Inicializa impressora
        if nome_impressora or colunas is not None:
            colunas_int = int(colunas) if colunas is not None else None
            impressora = ImpressoraTermica(impressora=nome_impressora, width_cols=colunas_int, usa_bematech=usa_bematech)
        else:
            impressora = ImpressoraTermica(usa_bematech=usa_bematech)
        
        # Limpa buffer
        impressora.limpar_buffer()
        
        # Cabeçalho - Nome da Empresa (tamanho normal)
        nome_empresa = obter_nome_empresa()
        impressora.adicionar_linha()
        impressora.adicionar_linha(nome_empresa, centralizar=True, negrito=True)
        impressora.adicionar_linha()
        impressora.adicionar_separador("=")
        impressora.adicionar_linha()
        
        # Busca responsável e cliente do pedido (se tiver cod_pedido)
        nome_cliente_info = None
        if dados_produto.get('cod_pedido'):
            try:
                conn = conexao_ativa()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        P.Responsável,
                        C.[Nome Cliente]
                    FROM Pedidos P
                    LEFT JOIN Clientes C ON P.[Código Cliente] = C.[Código Cliente]
                    WHERE P.[Código Pedido] = ?
                """, dados_produto['cod_pedido'])
                row = cursor.fetchone()
                if row:
                    responsavel = row[0] if row[0] else None
                    nome_cliente = row[1] if row[1] else None
                    # Prioridade: responsável primeiro, depois cliente
                    if responsavel and responsavel.strip():
                        nome_cliente_info = responsavel.strip()
                    elif nome_cliente and nome_cliente.strip():
                        nome_cliente_info = nome_cliente.strip()
                conn.close()
            except Exception as e:
                print(f"⚠️ Erro ao buscar responsável/cliente do pedido: {e}")
        
        # Exibe código do pedido e cliente/responsável se tiver
        if dados_produto.get('cod_pedido'):
            impressora.adicionar_linha(f"Pedido: {dados_produto['cod_pedido']}")
        if nome_cliente_info:
            impressora.adicionar_linha(f"Cliente: {nome_cliente_info[:impressora.width_cols-9]}")
        if dados_produto.get('cod_pedido') or nome_cliente_info:
            impressora.adicionar_linha()
        
        # Quantidade (em destaque)
        quantidade = dados_produto.get('quantidade', 0)
        impressora.adicionar_linha(f"QUANTIDADE: {quantidade:.2f}", negrito=True)
        impressora.adicionar_linha()
        
        # Descrição do produto (em tamanho médio, negrito) - quebra automática por pixels
        descricao = dados_produto.get('descricao', 'PRODUTO')
        # Usa tamanho_medio para que a função de desenho faça a quebra inteligente por pixels
        impressora.adicionar_linha(descricao, negrito=True, tamanho_medio=True)
        
        impressora.adicionar_linha()
        
        # Observação (se houver)
        observacao = dados_produto.get('observacao')
        if observacao and observacao.strip():
            # Quebra observação em múltiplas linhas se necessário
            palavras_obs = observacao.split()
            linha_atual = ""
            for palavra in palavras_obs:
                if len(linha_atual + " " + palavra) <= impressora.width_cols:
                    linha_atual += (" " if linha_atual else "") + palavra
                else:
                    if linha_atual:
                        impressora.adicionar_linha(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                impressora.adicionar_linha(linha_atual)
            impressora.adicionar_linha()
        
        # Hora de impressão
        hora_impressao = datetime.now().strftime("%H:%M:%S")
        impressora.adicionar_linha(f"Hora: {hora_impressao}")
        
        # Vendedor
        nome_vendedor = dados_produto.get('nome_vendedor', 'VENDEDOR')
        impressora.adicionar_linha(f"Vendedor: {nome_vendedor[:impressora.width_cols-10]}")
        
        # Rodapé
        impressora.adicionar_linha()
        impressora.adicionar_linha()
        
        # Envia para impressão
        return impressora._enviar_para_impressora()
        
    except Exception as e:
        print(f"❌ Erro ao imprimir ticket de produto: {e}")
        return False

 
 