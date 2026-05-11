#define MyAppName "Automacao Tracers Mind7"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Tracers"
#define MyAppExeName "AbrirAutomacaoTracersMind7.exe"

[Setup]
AppId={{A7F50D2B-5D5B-4A6E-8E91-7F50D2B5D5B7}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

PrivilegesRequired=admin

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=installer_dist
OutputBaseFilename=Instalador_Automacao_Tracers_Mind7

Compression=lzma
SolidCompression=yes
WizardStyle=modern

DisableProgramGroupPage=no
SetupLogging=yes

UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais:"; Flags: unchecked

[Files]
Source: "app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

Source: ".streamlit\*"; DestDir: "{app}\.streamlit"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "automations\*"; DestDir: "{app}\automations"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "installers\python-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "dist\AbrirAutomacaoTracersMind7.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\python-installer.exe"; Parameters: "/quiet InstallAllUsers=0 TargetDir=""{app}\python"" Include_pip=1 Include_launcher=0 PrependPath=0"; StatusMsg: "Instalando Python..."; Flags: waituntilterminated

Filename: "{app}\python\python.exe"; Parameters: "-m pip install --upgrade pip"; StatusMsg: "Atualizando pip..."; Flags: waituntilterminated

Filename: "{app}\python\python.exe"; Parameters: "-m pip install -r ""{app}\requirements.txt"""; StatusMsg: "Instalando bibliotecas..."; Flags: waituntilterminated

Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent