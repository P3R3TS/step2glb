@echo off
REM ============================================================================
REM Скрипт сборки step2glb для Windows
REM Build script for step2glb on Windows
REM
REM Конфигурация: build/build_config.json (читается через Python)
REM Configuration: build/build_config.json (read via Python)
REM
REM Использование / Usage:
REM   build\build_windows.bat              - Всё: .exe + установщик (по умолчанию)
REM   build\build_windows.bat both         - .exe + установщик
REM   build\build_windows.bat portable     - Только портативный .exe
REM   build\build_windows.bat installer    - Только установщик (Inno Setup)
REM   build\build_windows.bat onedir       - Сборка в папку
REM   build\build_windows.bat clean        - Очистка артефактов сборки
REM ============================================================================

setlocal enabledelayedexpansion

REM Читаем конфигурацию из build_config.json через Python
REM Read configuration from build_config.json via Python
for /f "delims=" %%i in ('python -c "import json; c=json.load(open('build/build_config.json')); print(c['app_name'])"') do set APP_NAME=%%i
for /f "delims=" %%i in ('python -c "import json; c=json.load(open('build/build_config.json')); print(c['entry_point'])"') do set ENTRY_POINT=%%i
for /f "delims=" %%i in ('python -c "import json; c=json.load(open('build/build_config.json')); print(c['ini_file'])"') do set INI_FILE=%%i
for /f "delims=" %%i in ('python -c "import json; c=json.load(open('build/build_config.json')); print(c['windows']['exe_name'])"') do set EXE_NAME=%%i

set MODE=%1
if "%MODE%"=="" set MODE=both
set VERSION=%2
if "%VERSION%"=="" set VERSION=dev

echo ============================================================
echo  %APP_NAME% build script for Windows (v%VERSION%)
echo  Mode: %MODE%
echo ============================================================
echo.

REM Переход в корень проекта / Change to project root
cd /d "%~dp0\.."

REM Проверка Python / Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [error] Python not found in PATH.
    echo Please install Python 3.8+ and add it to PATH.
    exit /b 1
)

REM Создание виртуального окружения / Create virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [build] Creating virtual environment...
    python -m venv .venv
)

REM Активация venv / Activate venv
call .venv\Scripts\activate.bat

REM Установка зависимостей / Install dependencies
echo [build] Installing dependencies...
pip install -r requirements.txt -q
pip install "pyinstaller>=5.0" -q

REM Очистка / Clean
if "%MODE%"=="clean" (
    echo [build] Cleaning build artifacts...
    if exist "dist" rmdir /s /q "dist"
    if exist "build\pyinstaller\build" rmdir /s /q "build\pyinstaller\build"
    if exist "installer" rmdir /s /q "installer"
    echo [build] Clean complete.
    goto :eof
)

REM Очистка предыдущей сборки / Clean previous build
if exist "dist\%EXE_NAME%" del /q "dist\%EXE_NAME%"

REM Проверка иконки / Check icon
set ICON_ARG=
if exist "icon.ico" set ICON_ARG=--icon icon.ico

REM ============================================================================
REM Сборка .exe / Build .exe
REM ============================================================================
if not "%MODE%"=="onedir" (
    echo [build] Building portable exe...
    pyinstaller --onefile --windowed --name %APP_NAME% %ICON_ARG% --clean --distpath dist %ENTRY_POINT%
    if errorlevel 1 (
        echo [error] Build failed.
        exit /b 1
    )
    echo [build] Portable exe: dist\%EXE_NAME%

    REM Копируем bat-лаунчер / Copy bat launcher
    if exist "%APP_NAME%.bat" copy /y "%APP_NAME%.bat" "dist\%APP_NAME%.bat"
)

REM Портативный архив / Portable archive
if "%MODE%"=="portable" (
    echo [build] Creating portable archive...
    powershell -Command "Compress-Archive -Path 'dist\%EXE_NAME%','dist\%APP_NAME%.bat' -DestinationPath 'dist\%APP_NAME%-%VERSION%-windows-portable.zip' -Force" 2>nul
    echo [build] Archive: dist\%APP_NAME%-%VERSION%-windows-portable.zip
)

REM ============================================================================
REM Сборка в папку / Build to directory
REM ============================================================================
if "%MODE%"=="onedir" (
    echo [build] Building directory distribution...
    pyinstaller --onedir --windowed --name %APP_NAME% %ICON_ARG% --clean --distpath dist %ENTRY_POINT%
    if errorlevel 1 (
        echo [error] Build failed.
        exit /b 1
    )
    echo [build] Directory: dist\%APP_NAME%\
)

REM ============================================================================
REM Установщик / Installer
REM ============================================================================
if "%MODE%"=="installer" goto :build_installer
if "%MODE%"=="both" goto :build_installer
goto :done

:build_installer
REM Проверяем Inno Setup / Check Inno Setup
REM Сначала в PATH / First check PATH
set ISCC_PATH=
where iscc >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('where iscc') do set ISCC_PATH=%%i
)

REM Если не в PATH — ищем в стандартных каталогах
REM If not in PATH — search common install directories
if "%ISCC_PATH%"=="" (
    for %%P in ("%ProgramFiles%" "%ProgramFiles(x86)%" "%LOCALAPPDATA%") do (
        for %%V in ("Inno Setup 7" "Inno Setup 6" "Inno Setup 5") do (
            if exist "%%~P\%%~V\ISCC.exe" set "ISCC_PATH=%%~P\%%~V\ISCC.exe"
        )
    )
)

if "%ISCC_PATH%"=="" (
    echo [warning] Inno Setup (iscc) not found.
    echo [warning] Searched: PATH, Program Files\Inno Setup 5-7
    echo [warning] Install from: https://jrsoftware.org/isinfo.php
    echo [warning] Or add ISCC.exe to PATH.
    echo [warning] Skipping installer build. Portable exe is ready.
    goto :done
)

echo.
echo [build] Building installer with Inno Setup... (%ISCC_PATH%)
cd build\inno_setup
"%ISCC_PATH%" installer_questions.iss
cd ..\..
if errorlevel 1 (
    echo [error] Installer build failed.
    goto :done
)
echo [build] Installer: installer\%APP_NAME%-setup-%VERSION%.exe

:done
echo.
echo ============================================================
echo  Build artifacts:
echo    dist\%EXE_NAME%              - Portable exe
echo    dist\%APP_NAME%-*.zip        - Portable archive
echo    installer\                   - Installer (if built)
echo ============================================================

endlocal
