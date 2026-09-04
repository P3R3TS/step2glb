# Инструкция по сборке и развёртыванию

## step2glb — Преобразователь STEP/IGES в GLB

---

**Версия документа:** 1.0  
**Дата:** Сентябрь 2026  
**Нормативные документы:** ГОСТ 19.201-78, ГОСТ 19.701-90  

---

## 1. Требования к среде разработки

| Компонент | Минимальная версия | Рекомендуемая |
|-----------|-------------------|---------------|
| Python | 3.8 | 3.11+ |
| pip | 20.0 | последняя |
| ОС | Windows 7 / Linux / macOS 10.14 | Windows 10+ |
| ОЗУ | 2 ГБ | 4 ГБ+ |
| Диск | 200 МБ | 500 МБ |

---

## 2. Установка зависимостей

### 2.1. Виртуальное окружение (рекомендуется)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2.2. Установка пакетов

```bash
pip install -r requirements.txt
```

### 2.3. Проверка установки

```bash
python -c "import cascadio; print('cascadio', cascadio.__version__)"
python -c "import tkinterdnd2; print('tkinterdnd2 OK')"
```

---

## 3. Запуск из исходников

```bash
python main.py
```

Или через пакет:

```bash
python -m src.main
```

---

## 4. Сборка через PyInstaller

### 4.1. Установка PyInstaller

```bash
pip install pyinstaller>=5.0
```

### 4.2. Быстрая сборка

```bash
pyinstaller --onefile --windowed --name step2glb main.py
```

### 4.3. Параметры сборки

| Параметр | Описание |
|----------|----------|
| `--onefile` | Единственный .exe файл |
| `--windowed` | Без консольного окна |
| `--name step2glb` | Имя выходного файла |
| `--icon=icon.ico` | Иконка приложения (опционально) |
| `--add-data "step2glb.ini;."` | Включение INI-файла (опционально) |
| `--onedir` | Сборка в папку (портативная, быстрый запуск) |

### 4.4. Полная сборка с иконкой и INI

```bash
pyinstaller --onefile --windowed --name step2glb ^
    --icon=icon.ico ^
    --add-data "step2glb.ini;." ^
    main.py
```

### 4.5. Сборка через скрипт

```bash
python build/pyinstaller/build_portable.py
```

### 4.6. Расположение результата

```
dist/
  step2glb.exe     ← исполняемый файл (~80–100 МБ)
```

---

## 5. Сборка установщика (Inno Setup)

### 5.1. Предварительные требования

- [Inno Setup 6+](https://jrsoftware.org/isinfo.php)
- `dist/step2glb.exe` (собран через PyInstaller)

### 5.2. Базовый установщик

```bash
cd build/inno_setup
iscc installer.iss
```

### 5.3. Установщик с дополнительными вопросами

```bash
iscc installer_questions.iss
```

Эта версия добавляет пользовательские запросы:
- Каталог установки
- Создание ярлыка на рабочем столе
- Папка в меню «Пуск»
- Привязка файлов (.stp, .step, .igs, .iges)

### 5.4. Результат

```
installer/
  step2glb-setup-x.x.x.exe     ← Windows-установщик
```

---

## 6. Скрипты сборки под разные ОС

### 6.1. Windows (портативная)

```bash
python build/build_all.py --platform windows --mode portable
```

Или напрямую:

```bat
build\build_windows.bat portable
```

### 6.2. Windows (установщик)

```bash
python build/build_all.py --platform windows --mode installer
```

Или напрямую:

```bat
build\build_windows.bat installer
```

### 6.3. Linux

```bash
python build/build_all.py --platform linux
```

Или напрямую:

```bash
chmod +x build/build_linux.sh
./build/build_linux.sh
```

### 6.4. macOS

```bash
python build/build_all.py --platform macos
```

Или напрямую:

```bash
chmod +x build/build_macos.sh
./build/build_macos.sh
```

### 6.5. Все платформы сразу

```bash
python build/build_all.py --all
```

---

## 7. Результаты сборки

| Платформа | Режим | Выход | Размер |
|-----------|-------|-------|--------|
| Windows | Портативная | `dist/step2glb.exe` | ~80–100 МБ |
| Windows | Установщик | `installer/step2glb-setup.exe` | ~80–100 МБ |
| Windows | Папка | `dist/step2glb/` | ~150 МБ |
| Linux | AppImage | `dist/step2glb.AppImage` | ~80–100 МБ |
| Linux | Папка | `dist/step2glb/` | ~150 МБ |
| macOS | App bundle | `dist/step2glb.app` | ~80–100 МБ |
| macOS | DMG | `dist/step2glb.dmg` | ~80–100 МБ |

---

## 8. Тестирование

### 8.1. Проверка импорта модулей

```bash
python -c "from src.config import PRESETS; print(PRESETS)"
python -c "from src.utils import has_non_ascii; print(has_non_ascii('test'))"
```

### 8.2. Проверка GUI

```bash
python main.py
```

### 8.3. Проверка собранного .exe

1. Запустите `dist/step2glb.exe`.
2. Выберите тестовый STEP/IGES файл.
3. Нажмите «Конвертировать».
4. Убедитесь, что `.glb` файл создан успешно.

---

## 9. Отладка

### 9.1. Вывод в консоль

Запуск из консоли для отладочного вывода (`.exe` с `--windowed` подавляет вывод):

```bash
python main.py
```

### 9.2. Просмотр архива PyInstaller

```bash
pyi-archive_viewer dist/step2glb.exe
```

---

## 10. Требования безопасности

- Программа не передаёт данные по сети.
- Все операции выполняются локально.
- Временные файлы удаляются при завершении.
- Код не содержит секретов и ключей.
