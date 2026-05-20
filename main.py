import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPoint
from PySide6.QtGui import (
    QFontDatabase,
    QPixmap,
    QPainter,
    QIcon,
    QColor,
    QPen,
    QPolygon,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QStackedWidget,
    QMessageBox,
    QGridLayout,
)


APP_VERSION = "1.10"

APP_WIDTH = 1180
APP_HEIGHT = 760

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
ASSETS_DIR = BASE_DIR / "assets"

APP_ICON = ASSETS_DIR / "hellocomp_icon.ico"

LOGO_CANDIDATES = [
    ASSETS_DIR / "hellocomp_logo.svg",
    ASSETS_DIR / "HELLOCOMP.svg",
    ASSETS_DIR / "hellocomp.svg",
    ASSETS_DIR / "logo.svg",
    ASSETS_DIR / "hellocomp_logo.png",
    ASSETS_DIR / "HELLOCOMP.png",
    ASSETS_DIR / "logo.png",
]

FONT_CANDIDATES = [
    ASSETS_DIR / "vafle.ttf",
    ASSETS_DIR / "vafle.OTF",
    ASSETS_DIR / "vafle.otf",
    ASSETS_DIR / "hellocomp_font.ttf",
    ASSETS_DIR / "hellocomp_font.otf",
]


SOFTWARE_INSTALLERS = {
    "steam": {
        "name": "Steam",
        "url": "https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe",
        "filename": "SteamSetup.exe",
        "fallback_url": "https://store.steampowered.com/about/",
        "exe_names": ["steam.exe"],
    },
    "discord": {
        "name": "Discord",
        "url": "https://discord.com/api/download?platform=win",
        "filename": "DiscordSetup.exe",
        "fallback_url": "https://discord.com/download",
        "exe_names": ["Discord.exe", "Update.exe"],
    },
}


TRANSLATIONS = {
    "cz": {
        "lang_label": "CZ",
        "window_title": "HelloComp Start",
        "header_title": "Můj počítač HelloComp",
        "header_subtitle": "První spuštění, podpora, servis a doporučený software",
        "footer": f"HelloComp.cz © 2026  |  verze {APP_VERSION}",
        "footer_social_title": "Sledujte nás",

        "menu": [
            "Můj počítač",
            "První kroky",
            "Potřebuji podporu",
            "Volitelný software",
            "Potřebuji servis",
        ],

        "my_pc_title": "Můj počítač",
        "my_pc_text": "Přehled hlavních informací o této sestavě.",
        "my_pc_refresh": "Načíst informace znovu",
        "my_pc_windows_only": "Detailní informace se automaticky načtou ve Windows verzi aplikace.",
        "my_pc_loading_error": "Informace se nepodařilo načíst.",

        "pc_fields": {
            "manufacturer": "Výrobce",
            "cpu": "Procesor",
            "gpu": "Grafická karta",
            "ram": "Operační paměť",
            "drives": "Disky",
            "baseboard": "Základní deska",
        },

        "first_steps_title": "První kroky s novým počítačem",
        "first_steps_text": "Pro váš nový počítač jsme připravili základní návody a doporučení.",
        "first_steps_tiles": [
            ("Návod k použití počítače", "Základní informace po prvním spuštění"),
            ("Aktivace Windows", "Jak ověřit aktivaci systému Windows"),
            ("Doporučené nastavení", "Tipy pro stabilní a plynulý provoz"),
        ],

        "support_title": "Potřebuji podporu",
        "support_text": "Jsme tu pro vás, pokud potřebujete poradit s počítačem, objednávkou nebo nastavením.",
        "support_tiles": [
            ("Kontaktovat podporu", "Otevřít kontaktní stránku HelloComp"),
            ("Napsat e-mail", "Rychlý kontakt na podporu"),
            ("Časté otázky", "Odpovědi na běžné dotazy"),
        ],

        "software_title": "Volitelný software",
        "software_text": "Vyberte si software, který se vám může hodit pro hraní, práci i správu počítače.",
        "software_tiles": [
            ("Instalovat Steam", "Stáhnout a spustit oficiální instalátor"),
            ("Instalovat Discord", "Stáhnout a spustit oficiální instalátor"),
            ("NVIDIA App", "Ovladače a nástroje pro nVidia grafiky"),
            ("AMD Adrenalin", "Ovladače a nástroje pro AMD grafiky"),
            ("Epic Games Launcher", "Otevřít oficiální stránku pro stažení"),
        ],

        "service_title": "Servis a reklamace",
        "service_text": "Potřebujete servis, údržbu nebo řešit reklamaci? Tady najdete potřebné odkazy.",
        "service_tiles": [
            ("Reklamace", "Informace k reklamaci zboží"),
            ("Servis počítače", "Pomoc s opravou nebo údržbou"),
            ("Bezpečné odeslání PC", "Jak správně zabalit počítač"),
        ],

        "install_only_windows": "Přímá instalace je dostupná ve Windows.\n\nNa tomto systému otevřu stránku pro stažení: {name}.",
        "installer_missing": "Instalátor nebyl nalezen.",
        "already_installed_title": "{name} je již nainstalovaný",
        "already_installed_text": "Aplikace {name} je už v počítači nainstalovaná.\n\nUmístění:\n{path}",
        "already_installed_no_path": "Aplikace {name} je už v počítači nainstalovaná.",
        "install_title": "Instalovat {name}",
        "install_question": "Aplikace stáhne oficiální instalátor {name} a spustí ho.\n\nPokračovat?",
        "download_title": "Stahuji {name}",
        "download_text": "Instalátor {name} se stahuje.\nPo dokončení se automaticky spustí.",
        "install_error_title": "Instalace {name}",
        "install_error_text": "Instalátor se nepodařilo stáhnout nebo spustit.\n\nOtevřu oficiální stránku pro stažení.\n\nChyba:\n{error}",
    },

    "sk": {
        "lang_label": "SK",
        "window_title": "HelloComp Start",
        "header_title": "Môj počítač HelloComp",
        "header_subtitle": "Prvé spustenie, podpora, servis a odporúčaný softvér",
        "footer": f"HelloComp.cz © 2026  |  verzia {APP_VERSION}",
        "footer_social_title": "Sledujte nás",

        "menu": [
            "Môj počítač",
            "Prvé kroky",
            "Potrebujem podporu",
            "Voliteľný softvér",
            "Potrebujem servis",
        ],

        "my_pc_title": "Môj počítač",
        "my_pc_text": "Prehľad hlavných informácií o tejto zostave.",
        "my_pc_refresh": "Načítať informácie znova",
        "my_pc_windows_only": "Detailné informácie sa automaticky načítajú vo Windows verzii aplikácie.",
        "my_pc_loading_error": "Informácie sa nepodarilo načítať.",

        "pc_fields": {
            "manufacturer": "Výrobca",
            "cpu": "Procesor",
            "gpu": "Grafická karta",
            "ram": "Operačná pamäť",
            "drives": "Disky",
            "baseboard": "Základná doska",
        },

        "first_steps_title": "Prvé kroky s novým počítačom",
        "first_steps_text": "Pre váš nový počítač sme pripravili základné návody a odporúčania.",
        "first_steps_tiles": [
            ("Návod na používanie počítača", "Základné informácie po prvom spustení"),
            ("Aktivácia Windows", "Ako overiť aktiváciu systému Windows"),
            ("Odporúčané nastavenia", "Tipy pre stabilnú a plynulú prevádzku"),
        ],

        "support_title": "Potrebujem podporu",
        "support_text": "Sme tu pre vás, ak potrebujete poradiť s počítačom, objednávkou alebo nastavením.",
        "support_tiles": [
            ("Kontaktovať podporu", "Otvoriť kontaktnú stránku HelloComp"),
            ("Napísať e-mail", "Rýchly kontakt na podporu"),
            ("Časté otázky", "Odpovede na bežné otázky"),
        ],

        "software_title": "Voliteľný softvér",
        "software_text": "Vyberte si softvér, ktorý sa vám môže hodiť na hranie, prácu aj správu počítača.",
        "software_tiles": [
            ("Inštalovať Steam", "Stiahnuť a spustiť oficiálny inštalátor"),
            ("Inštalovať Discord", "Stiahnuť a spustiť oficiálny inštalátor"),
            ("NVIDIA App", "Ovládače a nástroje pre nVidia grafiky"),
            ("AMD Adrenalin", "Ovládače a nástroje pre AMD grafiky"),
            ("Epic Games Launcher", "Otvoriť oficiálnu stránku na stiahnutie"),
        ],

        "service_title": "Servis a reklamácie",
        "service_text": "Potrebujete servis, údržbu alebo riešiť reklamáciu? Tu nájdete potrebné odkazy.",
        "service_tiles": [
            ("Reklamácie", "Informácie k reklamácii tovaru"),
            ("Servis počítača", "Pomoc s opravou alebo údržbou"),
            ("Bezpečné odoslanie PC", "Ako správne zabaliť počítač"),
        ],

        "install_only_windows": "Priama inštalácia je dostupná vo Windows.\n\nNa tomto systéme otvorím stránku na stiahnutie: {name}.",
        "installer_missing": "Inštalátor nebol nájdený.",
        "already_installed_title": "{name} je už nainštalovaný",
        "already_installed_text": "Aplikácia {name} je už v počítači nainštalovaná.\n\nUmiestnenie:\n{path}",
        "already_installed_no_path": "Aplikácia {name} je už v počítači nainštalovaná.",
        "install_title": "Inštalovať {name}",
        "install_question": "Aplikácia stiahne oficiálny inštalátor {name} a spustí ho.\n\nPokračovať?",
        "download_title": "Sťahujem {name}",
        "download_text": "Inštalátor {name} sa sťahuje.\nPo dokončení sa automaticky spustí.",
        "install_error_title": "Inštalácia {name}",
        "install_error_text": "Inštalátor sa nepodarilo stiahnuť alebo spustiť.\n\nOtvorím oficiálnu stránku na stiahnutie.\n\nChyba:\n{error}",
    },

    "hu": {
        "lang_label": "HU",
        "window_title": "HelloComp Start",
        "header_title": "Saját HelloComp számítógépem",
        "header_subtitle": "Első indítás, támogatás, szerviz és ajánlott szoftverek",
        "footer": f"HelloComp.cz © 2026  |  verzió {APP_VERSION}",
        "footer_social_title": "Kövessen minket",

        "menu": [
            "Saját gépem",
            "Első lépések",
            "Támogatásra van szükségem",
            "Választható szoftverek",
            "Szervizre van szükségem",
        ],

        "my_pc_title": "Saját gépem",
        "my_pc_text": "A számítógép fő adatainak áttekintése.",
        "my_pc_refresh": "Információk újratöltése",
        "my_pc_windows_only": "A részletes információk automatikusan betöltődnek a Windows verzióban.",
        "my_pc_loading_error": "Az információkat nem sikerült betölteni.",

        "pc_fields": {
            "manufacturer": "Gyártó",
            "cpu": "Processzor",
            "gpu": "Grafikus kártya",
            "ram": "Memória",
            "drives": "Meghajtók",
            "baseboard": "Alaplap",
        },

        "first_steps_title": "Első lépések az új számítógéppel",
        "first_steps_text": "Az új számítógépéhez alapvető útmutatókat és ajánlásokat készítettünk.",
        "first_steps_tiles": [
            ("Számítógép használati útmutató", "Alapvető információk az első indítás után"),
            ("Windows aktiválása", "A Windows aktiválásának ellenőrzése"),
            ("Ajánlott beállítások", "Tippek a stabil és gördülékeny működéshez"),
        ],

        "support_title": "Támogatásra van szükségem",
        "support_text": "Segítünk, ha tanácsra van szüksége a számítógéppel, a rendeléssel vagy a beállításokkal kapcsolatban.",
        "support_tiles": [
            ("Támogatás felkeresése", "A HelloComp kapcsolat oldalának megnyitása"),
            ("E-mail írása", "Gyors kapcsolat a támogatással"),
            ("Gyakori kérdések", "Válaszok a gyakori kérdésekre"),
        ],

        "software_title": "Választható szoftverek",
        "software_text": "Válassza ki azokat a szoftvereket, amelyek hasznosak lehetnek játékhoz, munkához és a számítógép kezeléséhez.",
        "software_tiles": [
            ("Steam telepítése", "Hivatalos telepítő letöltése és indítása"),
            ("Discord telepítése", "Hivatalos telepítő letöltése és indítása"),
            ("NVIDIA App", "Illesztőprogramok és eszközök nVidia grafikus kártyákhoz"),
            ("AMD Adrenalin", "Illesztőprogramok és eszközök AMD grafikus kártyákhoz"),
            ("Epic Games Launcher", "A hivatalos letöltési oldal megnyitása"),
        ],

        "service_title": "Szerviz és reklamáció",
        "service_text": "Szervizre, karbantartásra vagy reklamációra van szüksége? Itt megtalálja a szükséges hivatkozásokat.",
        "service_tiles": [
            ("Reklamáció", "Információk a termék reklamációjához"),
            ("Számítógép szerviz", "Segítség javításhoz vagy karbantartáshoz"),
            ("PC biztonságos küldése", "Hogyan csomagolja be helyesen a számítógépet"),
        ],

        "install_only_windows": "A közvetlen telepítés Windows alatt érhető el.\n\nEzen a rendszeren megnyitom a letöltési oldalt: {name}.",
        "installer_missing": "A telepítő nem található.",
        "already_installed_title": "A(z) {name} már telepítve van",
        "already_installed_text": "A(z) {name} alkalmazás már telepítve van a számítógépen.\n\nHely:\n{path}",
        "already_installed_no_path": "A(z) {name} alkalmazás már telepítve van a számítógépen.",
        "install_title": "{name} telepítése",
        "install_question": "Az alkalmazás letölti és elindítja a(z) {name} hivatalos telepítőjét.\n\nFolytatja?",
        "download_title": "{name} letöltése",
        "download_text": "A(z) {name} telepítője letöltődik.\nA letöltés után automatikusan elindul.",
        "install_error_title": "{name} telepítése",
        "install_error_text": "A telepítőt nem sikerült letölteni vagy elindítani.\n\nMegnyitom a hivatalos letöltési oldalt.\n\nHiba:\n{error}",
    },
}


def find_first_existing(paths):
    for path in paths:
        if path.exists():
            return path
    return None


def load_app_font():
    font_path = find_first_existing(FONT_CANDIDATES)

    if font_path:
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                print(f"✅ Font načten: {font_path}")
                print(f"✅ Font family: {families[0]}")
                return families[0]

        print(f"⚠️ Font existuje, ale nepodařilo se ho načíst: {font_path}")
    else:
        print("⚠️ Font nenalezen. Hledám zde:")
        for path in FONT_CANDIDATES:
            print(f" - {path}")

    return "Arial"


def find_logo():
    logo_path = find_first_existing(LOGO_CANDIDATES)

    if logo_path:
        print(f"✅ Logo nalezeno: {logo_path}")
        return logo_path

    print("⚠️ Logo nenalezeno. Hledám zde:")
    for path in LOGO_CANDIDATES:
        print(f" - {path}")

    return None


def is_windows():
    return platform.system().lower() == "windows"


def open_url(url):
    if url:
        webbrowser.open(url)


def run_powershell_json(command):
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
        timeout=25,
        encoding="utf-8",
        errors="replace",
    )

    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

    output = completed.stdout.strip()

    if not output:
        return None

    return json.loads(output)


def normalize_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def format_gb(bytes_value):
    try:
        return f"{round(int(bytes_value) / 1024 / 1024 / 1024)} GB"
    except Exception:
        return ""


def path_exists(path):
    try:
        return path and Path(path).exists()
    except Exception:
        return False


def find_steam_installation():
    if not is_windows():
        return None

    candidates = []

    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    program_files = os.environ.get("ProgramFiles")
    local_app_data = os.environ.get("LOCALAPPDATA")

    if program_files_x86:
        candidates.append(Path(program_files_x86) / "Steam" / "steam.exe")

    if program_files:
        candidates.append(Path(program_files) / "Steam" / "steam.exe")

    if local_app_data:
        candidates.append(Path(local_app_data) / "Steam" / "steam.exe")

    try:
        import winreg

        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamExe"),
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam", "InstallPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Valve\Steam", "InstallPath"),
        ]

        for root, key_path, value_name in registry_locations:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    if value:
                        value_path = Path(value)
                        if value_path.suffix.lower() == ".exe":
                            candidates.append(value_path)
                        else:
                            candidates.append(value_path / "steam.exe")
            except Exception:
                pass

    except Exception:
        pass

    for candidate in candidates:
        if path_exists(candidate):
            return str(candidate)

    return None


def find_discord_installation():
    if not is_windows():
        return None

    candidates = []

    local_app_data = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("ProgramFiles")
    program_files_x86 = os.environ.get("ProgramFiles(x86)")

    if local_app_data:
        discord_dir = Path(local_app_data) / "Discord"

        candidates.append(discord_dir / "Update.exe")

        if discord_dir.exists():
            try:
                app_dirs = sorted(
                    [
                        path
                        for path in discord_dir.iterdir()
                        if path.is_dir() and path.name.lower().startswith("app-")
                    ],
                    reverse=True
                )

                for app_dir in app_dirs:
                    candidates.append(app_dir / "Discord.exe")
            except Exception:
                pass

    if program_files:
        candidates.append(Path(program_files) / "Discord" / "Discord.exe")

    if program_files_x86:
        candidates.append(Path(program_files_x86) / "Discord" / "Discord.exe")

    for candidate in candidates:
        if path_exists(candidate):
            return str(candidate)

    return None


def find_installed_app(installer_key):
    if installer_key == "steam":
        return find_steam_installation()

    if installer_key == "discord":
        return find_discord_installation()

    return None


def open_installed_app(installer_key, app_path):
    if not is_windows() or not app_path:
        return

    try:
        if installer_key == "discord" and Path(app_path).name.lower() == "update.exe":
            subprocess.Popen([app_path, "--processStart", "Discord.exe"])
            return

        os.startfile(app_path)

    except Exception:
        pass


def get_windows_pc_info():
    script = r"""
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 Name
$gpus = Get-CimInstance Win32_VideoController | Select-Object Name
$ram = Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum
$drives = Get-CimInstance Win32_DiskDrive | Select-Object Model, Size, MediaType
$board = Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product

[PSCustomObject]@{
    Cpu = $cpu.Name
    Gpu = $gpus
    RamBytes = $ram.Sum
    Drives = $drives
    BoardManufacturer = $board.Manufacturer
    BoardProduct = $board.Product
} | ConvertTo-Json -Depth 5
"""

    data = run_powershell_json(script)

    gpus = []
    for gpu in normalize_list(data.get("Gpu")):
        name = gpu.get("Name") if isinstance(gpu, dict) else None
        if name:
            gpus.append(name)

    drives = []
    for drive in normalize_list(data.get("Drives")):
        if not isinstance(drive, dict):
            continue

        model = drive.get("Model") or ""
        size = format_gb(drive.get("Size"))
        media_type = drive.get("MediaType") or ""

        parts = [part for part in [model, size, media_type] if part]
        if parts:
            drives.append(" / ".join(parts))

    baseboard_parts = [
        data.get("BoardManufacturer"),
        data.get("BoardProduct"),
    ]

    return {
        "manufacturer": "HelloComp",
        "cpu": data.get("Cpu") or "—",
        "gpu": "\n".join(gpus) if gpus else "—",
        "ram": format_gb(data.get("RamBytes")) or "—",
        "drives": "\n".join(drives) if drives else "—",
        "baseboard": " ".join([x for x in baseboard_parts if x]) or "—",
    }


def get_pc_info(language):
    if is_windows():
        return get_windows_pc_info()

    t = TRANSLATIONS[language]

    return {
        "manufacturer": "HelloComp",
        "cpu": platform.processor() or platform.machine() or "—",
        "gpu": t["my_pc_windows_only"],
        "ram": t["my_pc_windows_only"],
        "drives": t["my_pc_windows_only"],
        "baseboard": t["my_pc_windows_only"],
    }


def download_and_run_installer(parent, installer_key, language):
    t = TRANSLATIONS[language]
    installer = SOFTWARE_INSTALLERS.get(installer_key)

    if not installer:
        QMessageBox.warning(parent, "Instalace", t["installer_missing"])
        return

    name = installer["name"]

    if not is_windows():
        webbrowser.open(installer["fallback_url"])
        return

    installed_path = find_installed_app(installer_key)

    if installed_path:
        QMessageBox.information(
            parent,
            t["already_installed_title"].format(name=name),
            t["already_installed_text"].format(name=name, path=installed_path)
        )
        open_installed_app(installer_key, installed_path)
        return

    reply = QMessageBox.question(
        parent,
        t["install_title"].format(name=name),
        t["install_question"].format(name=name),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )

    if reply != QMessageBox.Yes:
        return

    try:
        temp_dir = Path(tempfile.gettempdir()) / "HelloCompStart"
        temp_dir.mkdir(parents=True, exist_ok=True)

        installer_path = temp_dir / installer["filename"]

        request = urllib.request.Request(
            installer["url"],
            headers={
                "User-Agent": f"Mozilla/5.0 HelloCompStart/{APP_VERSION}"
            }
        )

        QMessageBox.information(
            parent,
            t["download_title"].format(name=name),
            t["download_text"].format(name=name)
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()

        if not data:
            raise RuntimeError("Stažený instalátor je prázdný.")

        installer_path.write_bytes(data)

        if not installer_path.exists() or installer_path.stat().st_size <= 0:
            raise RuntimeError("Instalátor se nepodařilo uložit.")

        if installer_path.suffix.lower() == ".msi":
            subprocess.Popen(["msiexec", "/i", str(installer_path)])
        else:
            os.startfile(str(installer_path))

    except Exception as error:
        QMessageBox.warning(
            parent,
            t["install_error_title"].format(name=name),
            t["install_error_text"].format(name=name, error=error)
        )
        webbrowser.open(installer["fallback_url"])


class SvgLogo(QLabel):
    def __init__(self, svg_path, width=310, height=88, scale_factor=0.76, y_offset=2):
        super().__init__()
        self.svg_path = str(svg_path)
        self.scale_factor = scale_factor
        self.y_offset = y_offset
        self.setObjectName("LogoImage")
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.render_svg()

    def render_svg(self):
        renderer = QSvgRenderer(self.svg_path)

        dpr = max(self.devicePixelRatioF(), 1.0)
        pixmap = QPixmap(int(self.width() * dpr), int(self.height() * dpr))
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)

        default_size = renderer.defaultSize()

        if default_size.width() <= 0 or default_size.height() <= 0:
            target = QRectF(0, 0, self.width(), self.height())
        else:
            scale = min(
                self.width() / default_size.width(),
                self.height() / default_size.height()
            ) * self.scale_factor

            target_width = default_size.width() * scale
            target_height = default_size.height() * scale

            x = (self.width() - target_width) / 2
            y = ((self.height() - target_height) / 2) + self.y_offset

            target = QRectF(x, y, target_width, target_height)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        renderer.render(painter, target)
        painter.end()

        self.setPixmap(pixmap)


class MenuButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(64)
        self.setCheckable(True)


class LangButton(QPushButton):
    def __init__(self, text, language):
        super().__init__(text)
        self.language = language
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setFixedHeight(34)
        self.setFixedWidth(78)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.isChecked():
            bg = QColor(255, 255, 255, 46)
            border = QColor(255, 255, 255, 96)
            text_color = QColor(255, 255, 255, 245)
        elif self.underMouse():
            bg = QColor(255, 255, 255, 30)
            border = QColor(255, 255, 255, 60)
            text_color = QColor(255, 255, 255, 230)
        else:
            bg = QColor(255, 255, 255, 18)
            border = QColor(255, 255, 255, 36)
            text_color = QColor(255, 255, 255, 190)

        painter.setPen(QPen(border, 1))
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 8, 8)

        flag_x = 10
        flag_y = int((self.height() - 12) / 2)
        flag_w = 18
        flag_h = 12

        self.draw_flag(painter, flag_x, flag_y, flag_w, flag_h)

        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(
            QRectF(36, 0, self.width() - 40, self.height()),
            Qt.AlignVCenter | Qt.AlignLeft,
            self.text()
        )

        painter.end()

    def draw_flag(self, painter, x, y, w, h):
        painter.setPen(Qt.NoPen)

        if self.language == "cz":
            painter.setBrush(QColor("#ffffff"))
            painter.drawRect(x, y, w, h // 2)

            painter.setBrush(QColor("#d7141a"))
            painter.drawRect(x, y + h // 2, w, h - h // 2)

            triangle = QPolygon([
                QPoint(x, y),
                QPoint(x + int(w * 0.52), y + int(h / 2)),
                QPoint(x, y + h),
            ])
            painter.setBrush(QColor("#11457e"))
            painter.drawPolygon(triangle)

        elif self.language == "sk":
            stripe = h // 3

            painter.setBrush(QColor("#ffffff"))
            painter.drawRect(x, y, w, stripe)

            painter.setBrush(QColor("#0b4ea2"))
            painter.drawRect(x, y + stripe, w, stripe)

            painter.setBrush(QColor("#ee1c25"))
            painter.drawRect(x, y + stripe * 2, w, h - stripe * 2)

        elif self.language == "hu":
            stripe = h // 3

            painter.setBrush(QColor("#ce2939"))
            painter.drawRect(x, y, w, stripe)

            painter.setBrush(QColor("#ffffff"))
            painter.drawRect(x, y + stripe, w, stripe)

            painter.setBrush(QColor("#477050"))
            painter.drawRect(x, y + stripe * 2, w, h - stripe * 2)


class SocialButton(QPushButton):
    def __init__(self, text, social_type):
        super().__init__(text)
        self.social_type = social_type
        self.setObjectName("FooterSocialButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(42)
        self.setMinimumWidth(118)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.underMouse():
            bg = QColor("#ffffff")
            border = QColor(36, 79, 136, 72)
            icon_bg = QColor("#244f88")
            icon_color = QColor("#ffffff")
        else:
            bg = QColor(255, 255, 255, 215)
            border = QColor(36, 79, 136, 36)
            icon_bg = QColor(36, 79, 136, 22)
            icon_color = QColor("#244f88")

        painter.setPen(QPen(border, 1))
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 10, 10)

        icon_rect = QRectF(14, 9, 24, 24)

        painter.setPen(Qt.NoPen)
        painter.setBrush(icon_bg)
        painter.drawRoundedRect(icon_rect, 7, 7)

        painter.setPen(icon_color)

        if self.social_type == "facebook":
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(18)
            painter.setFont(font)
            painter.drawText(icon_rect, Qt.AlignCenter, "f")

        elif self.social_type == "instagram":
            pen = QPen(icon_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(icon_rect.adjusted(6, 6, -6, -6), 4, 4)
            painter.drawEllipse(QRectF(icon_rect.center().x() - 3.5, icon_rect.center().y() - 3.5, 7, 7))
            painter.setBrush(icon_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(icon_rect.right() - 9, icon_rect.top() + 7, 3.2, 3.2))

        elif self.social_type == "discord":
            painter.setBrush(icon_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(icon_rect.left() + 5, icon_rect.top() + 7, 14, 9), 4, 4)
            painter.setBrush(icon_bg)
            painter.drawEllipse(QRectF(icon_rect.left() + 8, icon_rect.top() + 10, 2.6, 2.6))
            painter.drawEllipse(QRectF(icon_rect.left() + 13.5, icon_rect.top() + 10, 2.6, 2.6))

        font = painter.font()
        font.setBold(False)
        font.setPixelSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#244f88"))
        painter.drawText(
            QRectF(46, 0, self.width() - 52, self.height()),
            Qt.AlignVCenter | Qt.AlignLeft,
            self.text()
        )

        painter.end()


class TileButton(QPushButton):
    def __init__(self, title, subtitle, url=None, installer_key=None, language="cz"):
        super().__init__()
        self.url = url
        self.installer_key = installer_key
        self.language = language
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(128)
        self.update_text(title, subtitle)
        self.clicked.connect(self.handle_click)

    def update_text(self, title, subtitle):
        self.setText(f"{title}\n{subtitle}")

    def set_language(self, language):
        self.language = language

    def handle_click(self):
        if self.installer_key:
            download_and_run_installer(self.window(), self.installer_key, self.language)
            return

        if self.url:
            open_url(self.url)


class PcInfoCard(QFrame):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.setObjectName("PcInfoCard")
        self.setMinimumHeight(104)
        self.setMaximumHeight(118)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setObjectName("PcInfoTitle")

        self.value_label = QLabel()
        self.value_label.setObjectName("PcInfoValue")
        self.value_label.setWordWrap(True)
        self.value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def update_card(self, title, value):
        self.title_label.setText(title)
        self.value_label.setText(value or "—")


class HelloCompStart(QWidget):
    def __init__(self):
        super().__init__()

        self.language = "cz"
        self.app_font = load_app_font()
        self.logo_path = find_logo()

        self.setWindowTitle(TRANSLATIONS[self.language]["window_title"])
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        if APP_ICON.exists():
            self.setWindowIcon(QIcon(str(APP_ICON)))

        self.menu_buttons = []
        self.lang_buttons = []
        self.page_labels = {}
        self.tile_groups = {}
        self.pc_cards = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = self.create_header()
        menu = self.create_menu()

        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_my_pc_page())
        self.pages.addWidget(self.create_first_steps_page())
        self.pages.addWidget(self.create_support_page())
        self.pages.addWidget(self.create_software_page())
        self.pages.addWidget(self.create_service_page())

        self.footer = self.create_footer()

        root.addWidget(header)
        root.addWidget(menu)
        root.addWidget(self.pages)
        root.addWidget(self.footer)

        self.set_active_menu(0)
        self.apply_styles()
        self.update_language("cz")
        self.load_pc_information()

    def create_header(self):
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(146)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(44, 0, 44, 0)
        layout.setSpacing(24)

        left_wrapper_widget = QWidget()
        left_wrapper_widget.setObjectName("HeaderTextWrapper")

        left_wrapper = QVBoxLayout(left_wrapper_widget)
        left_wrapper.setContentsMargins(0, 0, 0, 0)
        left_wrapper.setSpacing(8)

        self.header_title = QLabel()
        self.header_title.setObjectName("HeaderTitle")

        self.header_subtitle = QLabel()
        self.header_subtitle.setObjectName("HeaderSubtitle")

        left_wrapper.addStretch()
        left_wrapper.addWidget(self.header_title)
        left_wrapper.addWidget(self.header_subtitle)
        left_wrapper.addStretch()

        right_wrapper = QWidget()
        right_wrapper.setObjectName("HeaderRightWrapper")

        right_layout = QVBoxLayout(right_wrapper)
        right_layout.setContentsMargins(0, 14, 0, 18)
        right_layout.setSpacing(8)

        lang_row = QWidget()
        lang_row.setObjectName("LangRow")

        lang_layout = QHBoxLayout(lang_row)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(7)
        lang_layout.addStretch()

        for language in ["cz", "sk", "hu"]:
            btn = LangButton(TRANSLATIONS[language]["lang_label"], language)
            btn.clicked.connect(lambda checked=False, lang=language: self.update_language(lang))
            self.lang_buttons.append(btn)
            lang_layout.addWidget(btn)

        logo_wrapper = QFrame()
        logo_wrapper.setObjectName("LogoWrapper")
        logo_wrapper.setFixedSize(330, 92)

        logo_layout = QVBoxLayout(logo_wrapper)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        if self.logo_path and self.logo_path.suffix.lower() == ".svg":
            logo = SvgLogo(self.logo_path, width=310, height=88, scale_factor=0.76, y_offset=2)
            logo_layout.addWidget(logo, alignment=Qt.AlignCenter)

        elif self.logo_path and self.logo_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            logo = QLabel()
            logo.setObjectName("LogoImage")

            pixmap = QPixmap(str(self.logo_path))
            logo.setPixmap(
                pixmap.scaled(
                    310,
                    88,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
            logo.setAlignment(Qt.AlignCenter)

            logo_layout.addWidget(logo, alignment=Qt.AlignCenter)

        else:
            logo = QLabel("HELLOCOMP")
            logo.setObjectName("LogoFallback")
            logo.setAlignment(Qt.AlignCenter)
            logo_layout.addWidget(logo)

        right_layout.addWidget(lang_row)
        right_layout.addWidget(logo_wrapper)

        layout.addWidget(left_wrapper_widget)
        layout.addStretch()
        layout.addWidget(right_wrapper)

        return header

    def create_footer(self):
        footer = QFrame()
        footer.setObjectName("Footer")
        footer.setFixedHeight(64)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(44, 0, 44, 0)
        footer_layout.setSpacing(20)

        self.footer_text = QLabel()
        self.footer_text.setObjectName("FooterText")
        self.footer_text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.footer_social_title = QLabel()
        self.footer_social_title.setObjectName("FooterSocialTitle")
        self.footer_social_title.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.footer_social = QWidget()
        self.footer_social.setObjectName("FooterSocial")

        footer_social_layout = QHBoxLayout(self.footer_social)
        footer_social_layout.setContentsMargins(0, 0, 0, 0)
        footer_social_layout.setSpacing(8)

        self.footer_facebook = SocialButton("Facebook", "facebook")
        self.footer_facebook.clicked.connect(lambda: open_url("https://www.facebook.com/HelloComp.cz"))

        self.footer_instagram = SocialButton("Instagram", "instagram")
        self.footer_instagram.clicked.connect(lambda: open_url("https://www.instagram.com/hellocompcz"))

        self.footer_discord = SocialButton("Discord", "discord")
        self.footer_discord.clicked.connect(lambda: open_url("https://discord.com/invite/dQDDXyek9x"))

        footer_social_layout.addWidget(self.footer_facebook)
        footer_social_layout.addWidget(self.footer_instagram)
        footer_social_layout.addWidget(self.footer_discord)

        footer_layout.addWidget(self.footer_text)
        footer_layout.addStretch()
        footer_layout.addWidget(self.footer_social_title)
        footer_layout.addWidget(self.footer_social)

        return footer

    def create_menu(self):
        menu = QFrame()
        menu.setObjectName("Menu")
        menu.setFixedHeight(64)

        layout = QHBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for index in range(5):
            btn = MenuButton()
            btn.clicked.connect(lambda checked=False, i=index: self.set_active_menu(i))
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        return menu

    def set_active_menu(self, index):
        self.pages.setCurrentIndex(index)

        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

    def create_my_pc_page(self):
        page = self.create_page_base("my_pc")

        top_row = QWidget()
        top_row.setObjectName("PcTopRow")

        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)

        self.refresh_pc_button = QPushButton()
        self.refresh_pc_button.setObjectName("RefreshPcButton")
        self.refresh_pc_button.setCursor(Qt.PointingHandCursor)
        self.refresh_pc_button.setFixedHeight(38)
        self.refresh_pc_button.clicked.connect(self.load_pc_information)

        top_layout.addStretch()
        top_layout.addWidget(self.refresh_pc_button)

        grid_wrapper = QWidget()
        grid_wrapper.setObjectName("PcGridWrapper")

        grid = QGridLayout(grid_wrapper)
        grid.setContentsMargins(0, 16, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        fields = [
            "manufacturer",
            "cpu",
            "gpu",
            "ram",
            "drives",
            "baseboard",
        ]

        for index, key in enumerate(fields):
            card = PcInfoCard(key)
            self.pc_cards[key] = card

            row = index // 3
            column = index % 3

            grid.addWidget(card, row, column)

        page.layout().addWidget(top_row)
        page.layout().addWidget(grid_wrapper)
        page.layout().addStretch()

        return page

    def create_first_steps_page(self):
        page = self.create_page_base("first_steps")
        tiles = self.create_tiles_row("first_steps", [
            ("https://www.hellocomp.cz/", None),
            ("https://www.hellocomp.cz/", None),
            ("https://www.hellocomp.cz/", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_support_page(self):
        page = self.create_page_base("support")
        tiles = self.create_tiles_row("support", [
            ("https://www.hellocomp.cz/kontakty/", None),
            ("mailto:info@hellocomp.cz", None),
            ("https://www.hellocomp.cz/", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_software_page(self):
        page = self.create_page_base("software")
        tiles = self.create_tiles_row("software", [
            (None, "steam"),
            (None, "discord"),
            ("https://www.nvidia.com/", None),
            ("https://www.amd.com/", None),
            ("https://store.epicgames.com/download", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_service_page(self):
        page = self.create_page_base("service")
        tiles = self.create_tiles_row("service", [
            ("https://www.hellocomp.cz/", None),
            ("https://www.hellocomp.cz/", None),
            ("https://www.hellocomp.cz/", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_page_base(self, key):
        page = QWidget()
        page.setObjectName("Page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 30, 50, 18)
        layout.setSpacing(15)

        title_label = QLabel()
        title_label.setObjectName("PageTitle")

        text_label = QLabel()
        text_label.setObjectName("PageText")
        text_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(text_label)

        self.page_labels[key] = {
            "title": title_label,
            "text": text_label,
        }

        return page

    def create_tiles_row(self, key, actions):
        wrapper = QWidget()
        wrapper.setObjectName("TilesWrapper")

        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(22)

        self.tile_groups[key] = []

        for url, installer_key in actions:
            tile = TileButton("", "", url, installer_key, self.language)
            self.tile_groups[key].append(tile)
            layout.addWidget(tile)

        return wrapper

    def load_pc_information(self):
        t = TRANSLATIONS[self.language]

        try:
            info = get_pc_info(self.language)
        except Exception as error:
            info = {
                key: "—"
                for key in t["pc_fields"].keys()
            }
            info["manufacturer"] = "HelloComp"
            info["cpu"] = str(error)

        for key, card in self.pc_cards.items():
            title = t["pc_fields"].get(key, key)
            value = info.get(key, "—")
            card.update_card(title, value)

    def update_language(self, language):
        self.language = language
        t = TRANSLATIONS[language]

        self.setWindowTitle(t["window_title"])
        self.header_title.setText(t["header_title"])
        self.header_subtitle.setText(t["header_subtitle"])
        self.footer_text.setText(t["footer"])
        self.footer_social_title.setText(t["footer_social_title"])
        self.refresh_pc_button.setText(t["my_pc_refresh"])

        for index, text in enumerate(t["menu"]):
            self.menu_buttons[index].setText(text)

        for btn in self.lang_buttons:
            btn.setChecked(btn.language == language)
            btn.update()

        page_keys = ["my_pc", "first_steps", "support", "software", "service"]

        for key in page_keys:
            self.page_labels[key]["title"].setText(t[f"{key}_title"])
            self.page_labels[key]["text"].setText(t[f"{key}_text"])

            if key in self.tile_groups:
                tiles_texts = t[f"{key}_tiles"]
                tiles = self.tile_groups[key]

                for tile, (title, subtitle) in zip(tiles, tiles_texts):
                    tile.update_text(title, subtitle)
                    tile.set_language(language)

        for key, card in self.pc_cards.items():
            card.title_label.setText(t["pc_fields"].get(key, key))

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: #0F1118;
                color: #ffffff;
                font-family: "{self.app_font}";
                font-size: 15px;
            }}

            #Header {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0F1118,
                    stop:0.50 #18243C,
                    stop:1 #284C87
                );
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }}

            #HeaderTextWrapper,
            #HeaderRightWrapper,
            #LangRow,
            #PcTopRow,
            #PcGridWrapper,
            #FooterSocial {{
                background: transparent;
            }}

            #HeaderTitle {{
                background: transparent;
                font-size: 28px;
                font-weight: 400;
                color: #ffffff;
                letter-spacing: 0.2px;
            }}

            #HeaderSubtitle {{
                background: transparent;
                font-size: 15px;
                font-weight: 400;
                color: rgba(255,255,255,0.72);
            }}

            #LogoWrapper {{
                background: transparent;
                border: none;
            }}

            #LogoImage {{
                background: transparent;
                border: none;
            }}

            #LogoFallback {{
                background: transparent;
                color: #ffffff;
                font-size: 28px;
                font-weight: 400;
                letter-spacing: 5px;
            }}

            #Menu {{
                background: #101d32;
                border-bottom: 3px solid #2f7fe0;
            }}

            QPushButton {{
                border: none;
                color: #ffffff;
                font-weight: 400;
            }}

            MenuButton {{
                background: rgba(15,17,24,0.34);
                color: rgba(255,255,255,0.76);
                border-right: 1px solid rgba(255,255,255,0.055);
                border-bottom: 3px solid transparent;
                font-size: 14px;
                font-weight: 400;
            }}

            MenuButton:hover {{
                background: rgba(255,255,255,0.065);
                color: #ffffff;
            }}

            MenuButton:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #18243C,
                    stop:1 #284C87
                );
                color: #ffffff;
                border-bottom: 3px solid #ffffff;
            }}

            LangButton {{
                background: transparent;
                border: none;
                color: transparent;
            }}

            #Page {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F1118,
                    stop:0.50 #18243C,
                    stop:1 #284C87
                );
            }}

            #PageTitle {{
                background: transparent;
                font-size: 29px;
                font-weight: 400;
                color: #ffffff;
                letter-spacing: 0.2px;
            }}

            #PageText {{
                background: transparent;
                font-size: 16px;
                font-weight: 400;
                color: rgba(255,255,255,0.74);
            }}

            #TilesWrapper {{
                background: transparent;
            }}

            TileButton {{
                background: rgba(255,255,255,0.075);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 13px;
                padding: 24px;
                text-align: left;
                font-size: 15px;
                font-weight: 400;
                line-height: 1.5;
                color: #ffffff;
            }}

            TileButton:hover {{
                background: rgba(255,255,255,0.13);
                border: 1px solid rgba(255,255,255,0.22);
            }}

            #PcInfoCard {{
                background: rgba(255,255,255,0.070);
                border: 1px solid rgba(255,255,255,0.115);
                border-radius: 12px;
            }}

            #PcInfoTitle {{
                background: transparent;
                color: rgba(255,255,255,0.60);
                font-size: 12px;
                font-weight: 400;
                letter-spacing: 0.02em;
            }}

            #PcInfoValue {{
                background: transparent;
                color: #ffffff;
                font-size: 14px;
                font-weight: 400;
                line-height: 1.30;
            }}

            #RefreshPcButton {{
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.16);
                border-radius: 10px;
                padding: 0 18px;
                color: #ffffff;
                font-size: 13px;
            }}

            #RefreshPcButton:hover {{
                background: rgba(255,255,255,0.17);
                border: 1px solid rgba(255,255,255,0.26);
            }}

            #Footer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc,
                    stop:1 #eef3f9
                );
                border-top: 1px solid #e3e8ef;
            }}

            #FooterText {{
                background: transparent;
                color: #3f4652;
                font-size: 13px;
                font-weight: 400;
            }}

            #FooterSocialTitle {{
                background: transparent;
                color: #5f6f82;
                font-size: 13px;
                font-weight: 400;
                letter-spacing: 0.02em;
            }}

            #FooterSocialButton {{
                background: transparent;
                border: none;
                color: #244f88;
                font-size: 13px;
                font-weight: 400;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if APP_ICON.exists():
        app.setWindowIcon(QIcon(str(APP_ICON)))

    window = HelloCompStart()
    window.show()

    sys.exit(app.exec())