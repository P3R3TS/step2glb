#!/usr/bin/env bash
# ============================================================================
# Скрипт сборки step2glb для macOS
# Build script for step2glb on macOS
#
# Использование / Usage:
#   ./build/build_macos.sh              - Портативная сборка
#   ./build/build_macos.sh portable     - Портативная сборка (onefile)
#   ./build/build_macos.sh app          - Сборка .app bundle
#   ./build/build_macos.sh dmg          - Сборка .dmg (требует app)
#   ./build/build_macos.sh clean        - Очистка
# ============================================================================

set -euo pipefail

# Конфигурация из build_config.sh / Config from build_config.sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/build_config.sh"

MODE="${1:-portable}"
VERSION="${2:-dev}"

# Переход в корень проекта / Change to project root
cd "$(dirname "$0")/.."

echo "============================================================"
echo " ${APP_NAME} build script for macOS (v${VERSION})"
echo " Mode: ${MODE}"
echo "============================================================"
echo

# Проверка Python / Check Python
if ! command -v python3 &>/dev/null; then
    echo "[error] python3 not found."
    echo "Install via: brew install python@3.11"
    exit 1
fi

PYTHON="python3"

# Создание виртуального окружения / Create virtual environment
if [ ! -f ".venv/bin/python" ]; then
    echo "[build] Creating virtual environment..."
    ${PYTHON} -m venv .venv
fi

# Активация / Activate
source .venv/bin/activate

# Установка зависимостей / Install dependencies
echo "[build] Installing dependencies..."
pip install -r requirements.txt -q
pip install "pyinstaller>=5.0" -q

# Очистка / Clean
if [ "${MODE}" = "clean" ]; then
    echo "[build] Cleaning build artifacts..."
    rm -rf dist/ build/pyinstaller/build/
    echo "[build] Clean complete."
    exit 0
fi

# Очистка предыдущей сборки / Clean previous build
rm -rf "dist/${APP_NAME}.app" "dist/${APP_NAME}"

case "${MODE}" in
    portable)
        echo "[build] Building portable binary..."
        pyinstaller --onefile --windowed --name "${APP_NAME}" \
            --clean --distpath dist "${ENTRY_POINT}"
        ;;

    app)
        echo "[build] Building .app bundle..."
        pyinstaller --onedir --windowed --name "${APP_NAME}" \
            --clean --distpath dist "${ENTRY_POINT}"

        # PyInstaller создаёт dist/${APP_NAME}, нужно в .app
        # PyInstaller creates dist/${APP_NAME}, need to wrap in .app
        if [ -d "dist/${APP_NAME}" ]; then
            APP_BUNDLE="dist/${APP_NAME}.app"
            mkdir -p "${APP_BUNDLE}/Contents/MacOS"
            mkdir -p "${APP_BUNDLE}/Contents/Resources"

            # Копируем бинарник / Copy binary
            cp "dist/${APP_NAME}/${APP_NAME}" "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

            # Копируем ресурсы / Copy resources
            cp -r "dist/${APP_NAME}/"* "${APP_BUNDLE}/Contents/MacOS/" 2>/dev/null || true

            # Info.plist / Info.plist
            cat > "${APP_BUNDLE}/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>${MACOS_BUNDLE_ID}</string>
    <key>CFBundleName</key>
    <string>step2glb</string>
    <key>CFBundleDisplayName</key>
    <string>step2glb</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>${MACOS_MIN_VERSION}</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST
            echo "[build] App bundle: ${APP_BUNDLE}"
        fi
        ;;

    dmg)
        # Сначала собираем .app / Build .app first
        if [ ! -d "dist/${APP_NAME}.app" ]; then
            echo "[build] Building .app bundle first..."
            $0 app
        fi

        echo "[build] Creating DMG..."
        if command -v hdiutil &>/dev/null; then
            DMG_NAME="${APP_NAME}-${VERSION}-macos.dmg"
            hdiutil create -volname "${APP_NAME}" \
                -srcfolder "dist/${APP_NAME}.app" \
                -ov -format UDZO \
                "dist/${DMG_NAME}"
            echo "[build] DMG: dist/${DMG_NAME}"
        else
            echo "[warning] hdiutil not found. Cannot create DMG."
            echo "[warning] .app bundle is ready at: dist/${APP_NAME}.app"
        fi
        ;;

    *)
        echo "[error] Unknown mode: ${MODE}"
        echo "Usage: $0 [portable|app|dmg|clean]"
        exit 1
        ;;
esac

# Результат / Output
if [ -f "dist/${APP_NAME}" ]; then
    SIZE=$(du -h "dist/${APP_NAME}" | cut -f1)
    echo
    echo "[build] Binary: dist/${APP_NAME} (${SIZE})"
fi

# ZIP архив / ZIP archive
if [ "${MODE}" = "portable" ] && [ -f "dist/${APP_NAME}" ]; then
    ARCHIVE="dist/${APP_NAME}-${VERSION}-macos-portable.zip"
    zip -j "${ARCHIVE}" "dist/${APP_NAME}"
    echo "[build] Archive: ${ARCHIVE}"
fi

echo
echo "============================================================"
echo " Build artifacts:"
echo "   dist/                            - Distribution files"
echo "============================================================"
