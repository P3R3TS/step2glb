# ============================================================================
# Конфигурация сборки (формат для shell-скриптов)
# Build configuration (shell-sourceable format)
#
# Использование / Usage:
#   source build/build_config.sh
# ============================================================================

APP_NAME="step2glb"
APP_DESCRIPTION="STEP/IGES to GLB converter"
APP_AUTHOR="step2glb contributors"
APP_URL="https://github.com/yourname/step2glb"
APP_LICENSE="MIT"

ENTRY_POINT="main.py"
INI_FILE="step2glb.ini"

ICON_ICO="icon.ico"
ICON_ICNS="icon.icns"
ICON_PNG="icon.png"

WIN_EXE="step2glb.exe"
WIN_ARCH="x64compatible"

MACOS_BUNDLE_ID="com.step2glb.app"
MACOS_MIN_VERSION="10.14"

LINUX_CATEGORIES="Development;Engineering;"
