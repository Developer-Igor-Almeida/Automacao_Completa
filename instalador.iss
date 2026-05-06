[Setup]
AppName=Automacao Tracers Mind7
AppVersion=1.0
AppPublisher=Automacao
DefaultDirName={autopf}\Automacao Tracers Mind7
DefaultGroupName=Automacao Tracers Mind7
OutputDir=instalador
OutputBaseFilename=Instalador_Automacao_Tracers_Mind7
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commondesktop}\Automacao Tracers Mind7"; Filename: "{app}\Automacao_Tracers_Mind7.exe"
Name: "{group}\Automacao Tracers Mind7"; Filename: "{app}\Automacao_Tracers_Mind7.exe"

[Run]
Filename: "{app}\Automacao_Tracers_Mind7.exe"; Description: "Abrir Automacao Tracers Mind7"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\tracers\saida"
Type: filesandordirs; Name: "{app}\mind7\entrada"
Type: filesandordirs; Name: "{app}\mind7\saida"
Type: filesandordirs; Name: "{app}\mind7\perfil_chrome"