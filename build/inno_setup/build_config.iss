; ============================================================================
; Конфигурация сборки (формат для Inno Setup)
; Build configuration (Inno Setup preprocessor format)
;
; Использование / Usage:
;   #include "build_config.iss"
; ============================================================================

#define MyAppName "step2glb"
#define MyAppVersion "1.0.0"
#define MyAppDescription "STEP/IGES to GLB converter"
#define MyAppPublisher "step2glb contributors"
#define MyAppURL "https://github.com/yourname/step2glb"
#define MyAppLicense "LICENSE"

#define MyAppExeName "step2glb.exe"
#define MyIniFile "step2glb.ini"
#define MyBatFile "step2glb.bat"

#define MyDistDir "..\..\dist"
#define MyOutputDir "..\..\installer"
#define MyAppCompression "zip"
