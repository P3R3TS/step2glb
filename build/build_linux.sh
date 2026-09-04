#!/usr/bin/env bash
# ============================================================================
# Скрипт сборки step2glb для Linux
# Build script for step2glb on Linux
#
# Использование / Usage:
#   ./build/build_linux.sh              - Портативная сборка
#   ./build/build_linux.sh portable     - Портативная сборка (onefile)
#   ./build/build_linux.sh onedir       - Сборка в папку
#   ./build/build_linux.sh appimage     - Сборка AppImage
#   ./build/build_linux.sh clean        - Очистка
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
echo " ${APP_NAME} build script for Linux (v${VERSION})"
echo " Mode: ${MODE}"
echo "============================================================"
echo

# Проверка Python / Check Python
if ! command -v python3 &>/dev/null; then
    echo "[error] python3 not found. Please install Python 3.8+."
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
rm -f "dist/${APP_NAME}"

case "${MODE}" in
    portable)
        echo "[build] Building portable binary..."
        pyinstaller --onefile --name "${APP_NAME}" --clean \
            --distpath dist --strip "${ENTRY_POINT}"
        ;;

    onedir)
        echo "[build] Building directory distribution..."
        pyinstaller --onedir --name "${APP_NAME}" --clean \
            --distpath dist --strip "${ENTRY_POINT}"
        ;;

    appimage)
        echo "[build] Building AppImage..."
        pyinstaller --onefile --name "${APP_NAME}" --clean \
            --distpath dist --strip "${ENTRY_POINT}"

        # Проверяем appimagetool / Check appimagetool
        if command -v appimagetool &>/dev/null; then
            echo "[build] Creating AppImage..."
            # Создаём AppDir структуру / Create AppDir structure
            APPDIR="dist/${APP_NAME}.AppDir"
            mkdir -p "${APPDIR}/usr/bin"
            mkdir -p "${APPDIR}/usr/share/applications"
            mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

            cp "dist/${APP_NAME}" "${APPDIR}/usr/bin/${APP_NAME}"

            # Desktop файл / Desktop file
            cat > "${APPDIR}/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=${APP_DESCRIPTION}
Exec=${APP_NAME}
Icon=${APP_NAME}
Categories=${LINUX_CATEGORIES}
Terminal=false
EOF

            # Иконка (заглушка) / Icon (placeholder)
            # В реальном проекте: cp icon.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"

            appimagetool "${APPDIR}" "dist/${APP_NAME}-${VERSION}-linux.AppImage"
            rm -rf "${APPDIR}"
            echo "[build] AppImage: dist/${APP_NAME}-${VERSION}-linux.AppImage"
        else
            echo "[warning] appimagetool not found. Skipping AppImage creation."
            echo "[warning] Install: https://github.com/AppImage/AppImageKit"
            echo "[warning] Portable binary is ready at: dist/${APP_NAME}"
        fi
        ;;

    *)
        echo "[error] Unknown mode: ${MODE}"
        echo "Usage: $0 [portable|onedir|appimage|clean]"
        exit 1
        ;;
esac

# Результат / Output
if [ -f "dist/${APP_NAME}" ]; then
    chmod +x "dist/${APP_NAME}"
    SIZE=$(du -h "dist/${APP_NAME}" | cut -f1)
    echo
    echo "[build] Build complete."
    echo "[build] Binary: dist/${APP_NAME} (${SIZE})"
fi

# Создание tar.gz / Create tar.gz
if [ "${MODE}" = "portable" ] && [ -f "dist/${APP_NAME}" ]; then
    ARCHIVE="dist/${APP_NAME}-${VERSION}-linux-portable.tar.gz"
    tar -czf "${ARCHIVE}" -C dist "${APP_NAME}"
    echo "[build] Archive: ${ARCHIVE}"
fi

echo
echo "============================================================"
echo " Build artifacts:"
echo "   dist/                            - Distribution files"
echo "============================================================"
