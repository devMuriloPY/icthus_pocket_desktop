# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de usuários do Windows
"""

import subprocess
import os


def listar_usuarios_windows():
    """Retorna uma lista com os usuários do Windows que podem fazer login."""
    try:
        # Usa o comando net user para listar usuários
        resultado = subprocess.run(
            ['net', 'user'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=True
        )
        
        if resultado.returncode == 0:
            linhas = resultado.stdout.split('\n')
            usuarios = []
            
            # Procura pela linha que contém os nomes de usuário
            # O formato do output pode variar por idioma:
            # PT: "Os nomes de conta de usuário são:"
            # EN: "User accounts for \\COMPUTER"
            # A linha seguinte contém os usuários separados por espaços
            iniciou_lista = False
            usuarios_sistema = ['Administrador', 'Administrator', 'Convidado', 'Guest', 
                               'DefaultAccount', 'WDAGUtilityAccount', 'DefaultUser']
            
            for i, linha in enumerate(linhas):
                linha = linha.strip()
                if not linha:
                    continue
                
                # Detecta quando começa a lista de usuários (várias formas possíveis)
                linha_lower = linha.lower()
                if any(keyword in linha_lower for keyword in ['nomes de conta', 'account names', 
                                                              'user accounts', 'usuários']):
                    iniciou_lista = True
                    # A próxima linha não vazia deve conter os usuários
                    continue
                
                if iniciou_lista:
                    # Verifica se a linha contém apenas separadores (como "----")
                    if linha.startswith('--') or linha.startswith('==='):
                        continue
                    
                    # Divide a linha em palavras e adiciona cada uma como usuário
                    palavras = linha.split()
                    for palavra in palavras:
                        palavra = palavra.strip()
                        # Ignora palavras vazias, separadores e usuários do sistema
                        if (palavra and 
                            not palavra.startswith('--') and 
                            not palavra.startswith('===') and
                            len(palavra) > 0 and
                            palavra not in usuarios_sistema):
                            usuarios.append(palavra)
                    
                    # Se encontrou usuários e a próxima linha parece ser um separador ou vazia, para
                    if usuarios and (i + 1 >= len(linhas) or not linhas[i + 1].strip() or 
                                     linhas[i + 1].strip().startswith('--')):
                        break
            
            # Remove duplicatas mantendo a ordem
            usuarios_unicos = []
            for usuario in usuarios:
                if usuario not in usuarios_unicos:
                    usuarios_unicos.append(usuario)
            
            # Se não encontrou usuários, adiciona pelo menos o atual
            if not usuarios_unicos:
                usuario_atual = obter_usuario_atual()
                if usuario_atual not in usuarios_sistema:
                    usuarios_unicos.append(usuario_atual)
            
            return usuarios_unicos if usuarios_unicos else [obter_usuario_atual()]
        else:
            # Se falhar, retorna pelo menos o usuário atual
            return [obter_usuario_atual()]
            
    except Exception as e:
        print(f"⚠️ Erro ao listar usuários do Windows: {e}")
        # Em caso de erro, retorna pelo menos o usuário atual
        return [obter_usuario_atual()]


def obter_usuario_atual():
    """Retorna o nome do usuário do Windows atualmente logado."""
    try:
        return os.environ.get("USERNAME", "Desconhecido")
    except Exception:
        return "Desconhecido"

