; Inno Setup скрипт для step2glb
; Inno Setup script for step2glb
;
; Базовая версия установщика / Basic installer version
;
; Конфигурация: inno_setup/build_config.iss
; Configuration: inno_setup/build_config.iss
;
; Использование: iscc installer.iss
; Usage: iscc installer.iss

#include "build_config.iss"

[Setup]
AppId={{B1E2C3D4-5678-9ABC-DEF0-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=..\..\{#MyAppLicense}
OutputDir={#MyOutputDir}
OutputBaseFilename={#MyAppName}-setup-{#MyAppVersion}
Compression={#MyAppCompression}
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoDescription={#MyAppName} installer
SetupIconFile=..\..\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyDistDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\{#MyBatFile}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\{#MyAppLicense}"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Регистрация расширений файлов / File association
Root: HKA; Subkey: "Software\Classes\.stp\OpenWithProgids"; ValueType: string; ValueName: "step2glb.stp"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.step\OpenWithProgids"; ValueType: string; ValueName: "step2glb.step"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.igs\OpenWithProgids"; ValueType: string; ValueName: "step2glb.igs"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.iges\OpenWithProgids"; ValueType: string; ValueName: "step2glb.iges"; ValueData: ""; Flags: uninsdeletevalue

Root: HKA; Subkey: "Software\Classes\step2glb.stp"; ValueType: string; ValueName: ""; ValueData: "STEP File (step2glb)"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\step2glb.stp\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\step2glb.stp\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKA; Subkey: "Software\Classes\step2glb.step"; ValueType: string; ValueName: ""; ValueData: "STEP File (step2glb)"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\step2glb.step\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\step2glb.step\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKA; Subkey: "Software\Classes\step2glb.igs"; ValueType: string; ValueName: ""; ValueData: "IGES File (step2glb)"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\step2glb.igs\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\step2glb.igs\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKA; Subkey: "Software\Classes\step2glb.iges"; ValueType: string; ValueName: ""; ValueData: "IGES File (step2glb)"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\step2glb.iges\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\step2glb.iges\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
