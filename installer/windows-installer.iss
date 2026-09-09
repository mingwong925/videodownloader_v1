[Setup]
AppName=片刻
AppVersion=1.0.0
DefaultDirName={autopf}\Pianke
DefaultGroupName=片刻
OutputDir=installer-output
OutputBaseFilename=Pianke-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=assets\icon.ico

[Files]
Source: "dist\Pianke\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\片刻"; Filename: "{app}\Pianke.exe"
Name: "{autodesktop}\片刻"; Filename: "{app}\Pianke.exe"

[Run]
Filename: "{app}\Pianke.exe"; Description: "啟動片刻"; Flags: nowait postinstall skipifsilent