# Guia de Compilação - ICThUS Pocket Desktop

## 📦 Compilando o Executável

Este guia explica como compilar o aplicativo ICThUS Pocket Desktop em um executável Windows (.exe) independente.

## ✅ Pré-requisitos

1. **Python 3.11+** instalado
2. **Ambiente virtual (venv)** ativado
3. **Todas as dependências instaladas**:
   ```bash
   pip install -r requirements.txt
   ```
4. **PyInstaller instalado** (já está no requirements.txt):
   ```bash
   pip install pyinstaller
   ```

## 🔧 Preparação

### 1. Instalar pywin32 na venv
```bash
# Ative a venv primeiro
.\venv\Scripts\activate

# Instale o pywin32
pip install pywin32

# IMPORTANTE: Execute o script de pós-instalação
python -m pywin32_postinstall -install
```

### 2. Verificar a instalação
```bash
python -c "import win32print; print('pywin32 OK')"
```

Se não houver erros, está pronto para compilar.

## 🚀 Compilando

### Método 1: Usando o app.spec (Recomendado)

```bash
# Certifique-se de estar na pasta raiz do projeto
cd C:\icthus_pocket\pocket_desktop

# Ative a venv
.\venv\Scripts\activate

# Compile usando o spec file
pyinstaller app.spec --clean --noconfirm
```

### Método 2: Comando direto (menos recomendado)

```bash
pyinstaller --name="ICThUS Pocket Sync" ^
    --windowed ^
    --onefile ^
    --icon=assets/images/app_icon.ico ^
    --add-data="assets/images;assets/images" ^
    --hidden-import=win32print ^
    --hidden-import=win32ui ^
    main.py
```

## 📁 Resultado da Compilação

Após a compilação bem-sucedida, você encontrará:

```
pocket_desktop/
├── build/              # Arquivos temporários de build
├── dist/               # ← EXECUTÁVEIS AQUI
│   ├── ICThUS Pocket Sync/      # Versão com dependências separadas
│   │   ├── ICThUS Pocket Sync.exe
│   │   └── _internal/           # DLLs e dependências
│   └── ICThUS Pocket Sync.exe   # Executável único (se usar --onefile)
└── app.spec            # Arquivo de configuração
```

## 🔍 Verificando o Executável

### 1. Teste básico
Navegue até `dist/ICThUS Pocket Sync/` e execute:
```
"ICThUS Pocket Sync.exe"
```

### 2. Verifique o módulo pywin32
O aplicativo deve:
- Abrir normalmente
- WebSocket iniciar automaticamente
- **NÃO** exibir erros sobre "módulos win32 não disponíveis"

## ⚙️ Configuração do app.spec

O arquivo `app.spec` já está configurado com:

### Módulos pywin32 incluídos:
```python
hiddenimports=[
    # ... outros módulos ...
    "win32print",
    "win32ui",
    "win32api",
    "win32con",
]
```

### DLLs do pywin32:
```python
pywin32_datas = collect_data_files('pywin32_system32')
pywin32_binaries = collect_dynamic_libs('pywin32_system32')
```

## ⚠️ Problemas Comuns

### Erro: "No module named 'win32print'"

**Causa**: pywin32 não foi incluído no executável

**Solução**:
1. Verifique se pywin32 está instalado na venv
2. Execute `python -m pywin32_postinstall -install`
3. Recompile com `--clean`

### Erro: "DLL load failed"

**Causa**: DLLs do pywin32 não foram copiadas

**Solução**:
1. Use o `app.spec` fornecido (já configurado)
2. Certifique-se que `collect_dynamic_libs` está funcionando
3. Copie manualmente as DLLs de `venv\Lib\site-packages\pywin32_system32\` para `dist\_internal\`

### Executável muito grande

**Causa**: PyInstaller inclui muitas dependências

**Soluções**:
- Use UPX para comprimir (já habilitado no spec)
- Revise os `excludes` no app.spec
- Use versão "folder" ao invés de "onefile"

### Antivírus bloqueia o executável

**Causa**: Falso positivo comum com PyInstaller

**Soluções**:
- Adicione exceção no antivírus
- Assine digitalmente o executável
- Use instalador oficial (NSIS/Inno Setup)

## 📊 Tamanho Esperado

- **Versão onefile**: ~80-120 MB
- **Versão folder**: Similar, mas distribuído entre vários arquivos
- Com UPX ativo: redução de 20-30%

## 🔄 Recompilando após Mudanças

Sempre use `--clean` para evitar problemas de cache:

```bash
pyinstaller app.spec --clean --noconfirm
```

## 📝 Testando antes da Distribuição

### Checklist de Testes:

- [ ] Aplicativo abre normalmente
- [ ] Interface carrega corretamente
- [ ] Ícones e imagens aparecem
- [ ] Conexão com banco de dados funciona
- [ ] WebSocket inicia automaticamente
- [ ] Impressão funciona corretamente
- [ ] Aplicação minimiza para bandeja
- [ ] Aplicação fecha corretamente

## 📦 Criando Instalador (Opcional)

Após compilar o executável, você pode criar um instalador usando:

### Inno Setup
```batch
cd instalador
iscc script_iss.iss
```

O instalador será criado em `instalador/output/`

## 🎯 Distribuição Final

### O que distribuir:

**Opção 1: Pasta completa**
```
dist/ICThUS Pocket Sync/
```
Comprima em ZIP e distribua

**Opção 2: Instalador**
```
instalador/output/ICThUS Pocket - Instalador.exe
```
Distribua o instalador direto

## 🔒 Notas de Segurança

1. **Firewall**: Pode solicitar permissão para o WebSocket
2. **Assinatura Digital**: Recomendada para distribuição profissional

## 📞 Suporte

Se encontrar problemas durante a compilação:
1. Verifique se a venv está ativada
2. Delete as pastas `build` e `dist`
3. Recompile com `--clean`
4. Verifique os logs em `build/app/warn-app.txt`

---
**Última atualização**: 2025-11-07

