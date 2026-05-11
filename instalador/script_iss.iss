; ICThUS Pocket Sync - Inno Setup Script (modo multi-arquivo)

[Setup]
AppName=ICThUS Pocket Sync
AppVersion=1.0
DefaultDirName={commonpf}\ICThUS Pocket Sync
DefaultGroupName=ICThUS Pocket Sync
OutputDir=output
OutputBaseFilename=ICThUS Pocket - Instalador
SetupIconFile=C:\Projetos\WM\Python\icthus_pocket_desktop\instalador\setup.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
AllowNoIcons=yes

[Files]
; Copia todos os arquivos da pasta "dist\ICThUS Pocket Sync"
Source: "C:\Projetos\WM\Python\icthus_pocket_desktop\dist\ICThUS Pocket Sync\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ICThUS Pocket Sync"; Filename: "{app}\ICThUS Pocket Sync.exe"
Name: "{commondesktop}\ICThUS Pocket Sync"; Filename: "{app}\ICThUS Pocket Sync.exe"; Tasks: desktopicon
Name: "{commonstartup}\ICThUS Pocket Sync"; Filename: "{app}\ICThUS Pocket Sync.exe"; Tasks: autostart

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho (todos os usuários)"; GroupDescription: "Atalhos:"
Name: "autostart"; Description: "Iniciar automaticamente com o Windows (todos os usuários)"; GroupDescription: "Inicialização automática:"

[Run]
Filename: "{app}\ICThUS Pocket Sync.exe"; Description: "Executar ICThUS Pocket Sync agora"; Flags: nowait postinstall skipifsilent
