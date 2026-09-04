; Inno Setup скрипт для step2glb с дополнительными вопросами
; Inno Setup script for step2glb with custom wizard questions
;
; Конфигурация: inno_setup/build_config.iss
; Configuration: inno_setup/build_config.iss
;
; Использование: iscc installer_questions.iss
; Usage: iscc installer_questions.iss

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
#if FileExists("..\..\icon.ico")
SetupIconFile=..\..\icon.ico
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

; ============================================================================
; Задачи (пользовательские вопросы) / Tasks (user questions)
; ============================================================================

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе / Create desktop shortcut"; GroupDescription: "Дополнительно / Additional:"; Flags: unchecked
Name: "startmenuicon"; Description: "Добавить в меню «Пуск» / Add to Start Menu"; GroupDescription: "Дополнительно / Additional:"; Flags: checkedonce
Name: "associatefiles"; Description: "Привязать файлы .stp/.step/.igs/.iges / Associate STEP/IGES files"; GroupDescription: "Файловые ассоциации / File associations:"; Flags: unchecked
Name: "launchafter"; Description: "Запустить после установки / Launch after install"; GroupDescription: "Запуск / Launch:"; Flags: checkedonce

; ============================================================================
; Файлы / Files
; ============================================================================

[Files]
Source: "{#MyDistDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\{#MyBatFile}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\{#MyAppLicense}"; DestDir: "{app}"; Flags: ignoreversion isreadme

; ============================================================================
; Ярлыки / Shortcuts
; ============================================================================

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Tasks: startmenuicon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ============================================================================
; Запуск / Post-install launch
; ============================================================================

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName} / Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent; Tasks: launchafter

; ============================================================================
; Регистрация расширений (опционально) / File associations (optional)
; ============================================================================

[Registry]
Root: HKA; Subkey: "Software\Classes\.stp\OpenWithProgids"; ValueType: string; ValueName: "step2glb.stp"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\.step\OpenWithProgids"; ValueType: string; ValueName: "step2glb.step"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\.igs\OpenWithProgids"; ValueType: string; ValueName: "step2glb.igs"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\.iges\OpenWithProgids"; ValueType: string; ValueName: "step2glb.iges"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatefiles

Root: HKA; Subkey: "Software\Classes\step2glb.stp"; ValueType: string; ValueName: ""; ValueData: "STEP File (step2glb)"; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.stp\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.stp\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatefiles

Root: HKA; Subkey: "Software\Classes\step2glb.step"; ValueType: string; ValueName: ""; ValueData: "STEP File (step2glb)"; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.step\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.step\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatefiles

Root: HKA; Subkey: "Software\Classes\step2glb.igs"; ValueType: string; ValueName: ""; ValueData: "IGES File (step2glb)"; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.igs\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.igs\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatefiles

Root: HKA; Subkey: "Software\Classes\step2glb.iges"; ValueType: string; ValueName: ""; ValueData: "IGES File (step2glb)"; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.iges\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\step2glb.iges\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatefiles

; ============================================================================
; События установки / Install events
; ============================================================================

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Опционально / Optionally
  end;
end;
