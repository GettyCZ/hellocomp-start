import ctypes
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import urllib.request
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPoint, QTimer
from PySide6.QtGui import (
    QFontDatabase,
    QPixmap,
    QPainter,
    QIcon,
    QColor,
    QPen,
    QPolygon,
    QFont,
    QLinearGradient,
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


APP_VERSION = "2.0-beta12"

APP_WIDTH = 1180
APP_HEIGHT = 760

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
ASSETS_DIR = BASE_DIR / "assets"

APP_ICON = ASSETS_DIR / "hellocomp_icon.ico"
WALLPAPER_FILE = ASSETS_DIR / "HelloCompwallpaper.png"

GITHUB_RELEASES_URL = "https://github.com/GettyCZ/hellocomp-start/releases/latest"
VERSION_MANIFEST_URL = "https://github.com/GettyCZ/hellocomp-start/releases/latest/download/version.json"

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

FA_BRANDS_CANDIDATES = [
    ASSETS_DIR / "fa-brands-400.ttf",
    ASSETS_DIR / "fa-brands-400.otf",
    ASSETS_DIR / "Font Awesome 6 Brands-Regular-400.otf",
    ASSETS_DIR / "Font Awesome 6 Brands-Regular-400.ttf",
    ASSETS_DIR / "Font Awesome 5 Brands-Regular-400.otf",
    ASSETS_DIR / "Font Awesome 5 Brands-Regular-400.ttf",
]


SOFTWARE_INSTALLERS = {
    "steam": {
        "name": "Steam",
        "url": "https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe",
        "filename": "SteamSetup.exe",
        "fallback_url": "https://store.steampowered.com/about/",
    },
    "discord": {
        "name": "Discord",
        "url": "https://discord.com/api/download?platform=win",
        "filename": "DiscordSetup.exe",
        "fallback_url": "https://discord.com/download",
    },
}


SOFTWARE_URLS = {
    "nvidia": "https://www.nvidia.com/en-us/software/nvidia-app/",
    "amd": "https://www.amd.com/en/products/software/adrenalin.html",
    "intel": "https://www.intel.com/content/www/us/en/download/785597/intel-arc-graphics-windows.html",
    "epic": "https://store.epicgames.com/download",
    "occt": "https://www.ocbase.com/",
}


DRIVER_NAMES = {
    "nvidia": "nVidia App",
    "amd": "AMD Adrenalin",
    "intel": "Intel Graphics",
}


def is_windows():
    return platform.system().lower() == "windows"


def is_frozen_exe():
    return bool(getattr(sys, "frozen", False))


def get_settings_dir():
    if is_windows():
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "HelloComp Start"

    return APP_DIR


SETTINGS_DIR = get_settings_dir()
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


TRANSLATIONS = {
    "cz": {
        "lang_label": "CZ",
        "window_title": "HelloComp Start",
        "header_title": "Můj počítač HelloComp",
        "header_subtitle": "Rychlý start, doporučené aplikace, podpora a servis na jednom místě.",
        "footer": f"HelloComp.cz © 2026  |  verze {APP_VERSION}",
        "footer_social_title": "Sledujte nás",
        "recommended_badge": "Doporučeno pro tento PC",

        "settings": "Nastavení",
        "settings_title": "Nastavení aplikace",
        "settings_subtitle": "Jazyk, tapeta, aktualizace a základní informace.",
        "settings_language": "Jazyk aplikace",
        "settings_wallpaper": "Tapeta HelloComp",
        "settings_wallpaper_text": "Nastaví připravenou HelloComp tapetu na plochu Windows.",
        "settings_wallpaper_button": "Nastavit tapetu",
        "settings_update": "Aktualizace aplikace",
        "settings_update_text": "Zkontroluje, jestli je dostupná novější verze aplikace HelloComp Start.",
        "settings_update_button": "Vyhledat aktualizaci aplikace",
        "settings_about": "O aplikaci",
        "settings_about_text": f"Oficiální aplikace HelloComp Start. Verze {APP_VERSION}.",

        "update_check_title": "Aktualizace aplikace",
        "update_checking": "Kontroluji dostupnost nové verze…",
        "update_latest_title": "Aplikace je aktuální",
        "update_latest_text": f"Používáte nejnovější verzi aplikace HelloComp Start ({APP_VERSION}).",
        "update_available_title": "Je dostupná nová verze",
        "update_available_text": "Je dostupná nová verze aplikace HelloComp Start.\n\nAktuální verze: {current}\nNová verze: {latest}\n\nChcete ji stáhnout a nainstalovat?",
        "update_download_title": "Stahuji aktualizaci",
        "update_download_text": "Nová verze se stáhne a aplikace se poté automaticky restartuje.",
        "update_error_title": "Aktualizace se nezdařila",
        "update_error_text": "Aktualizaci se nepodařilo ověřit nebo stáhnout.\n\nChyba:\n{error}",
        "update_dev_title": "Automatická aktualizace",
        "update_dev_text": "Automatické přepsání aplikace funguje pouze ve Windows .exe verzi.\n\nTeď otevřu stránku se stažením nové verze.",

        "settings_wallpaper_success_title": "Tapeta nastavena",
        "settings_wallpaper_success_text": "Tapeta HelloComp byla nastavena.",
        "settings_wallpaper_missing_title": "Tapeta nenalezena",
        "settings_wallpaper_missing_text": "Soubor assets/HelloCompwallpaper.png nebyl nalezen.",
        "settings_wallpaper_windows_only_title": "Tapeta",
        "settings_wallpaper_windows_only_text": "Automatické nastavení tapety je dostupné ve Windows verzi aplikace.",

        "wrong_driver_title": "Tento ovladač není doporučený",
        "wrong_driver_text": "Aplikace detekovala grafickou kartu {detected}. Pro tento počítač je doporučený ovladač {recommended}.\n\nChcete i přesto otevřít stránku {selected}?",
        "gpu_unknown_title": "Grafická karta nebyla jednoznačně rozpoznána",
        "gpu_unknown_text": "Aplikace nedokázala jednoznačně určit výrobce grafické karty. Otevřete pouze ovladač, který odpovídá vaší grafické kartě.",

        "menu": ["Můj počítač", "První kroky", "Podpora", "Aplikace", "Servis"],

        "my_pc_title": "Můj počítač",
        "my_pc_text": "Přehled hlavních parametrů sestavy. Detailní hardwarové údaje se načtou automaticky ve Windows.",
        "my_pc_refresh": "Načíst znovu",
        "my_pc_loading": "Načítám…",
        "my_pc_windows_only": "Detailní informace se automaticky načtou ve Windows verzi aplikace.",

        "pc_fields": {
            "manufacturer": "Výrobce",
            "cpu": "Procesor",
            "gpu": "Grafická karta",
            "ram": "Operační paměť",
            "drives": "Disky",
            "baseboard": "Základní deska",
        },

        "first_steps_title": "První kroky",
        "first_steps_text": "Doporučené kroky po prvním spuštění počítače.",
        "first_steps_tiles": [
            ("📘 Návod k použití", "Základní informace po prvním spuštění"),
            ("🪟 Aktivace Windows", "Ověření aktivace systému Windows"),
            ("⚙️ Doporučené nastavení", "Tipy pro stabilní provoz"),
        ],

        "support_title": "Podpora HelloComp",
        "support_text": "Rychlá pomoc, kontakt a odpovědi na nejčastější dotazy.",
        "support_tiles": [
            ("☎️ Kontakt", "Otevřít kontaktní stránku HelloComp"),
            ("✉️ Napsat e-mail", "info@hellocomp.cz"),
            ("❔ Časté otázky", "FAQ a odpovědi na běžné dotazy"),
        ],

        "software_title": "Doporučené aplikace",
        "software_text": "Aplikace pro hraní, komunikaci, ovladače, správu počítače a základní test stability.",
        "software_tiles": [
            ("🎮 Steam", "Stáhnout a spustit instalátor"),
            ("💬 Discord", "Stáhnout a spustit instalátor"),
            ("🕹️ Epic Games", "Otevřít stránku ke stažení"),
            ("🧪 OCCT", "Test stability CPU, GPU, RAM a zdroje"),
            ("🟢 nVidia App", "Oficiální aplikace a ovladače nVidia"),
            ("🔴 AMD Adrenalin", "Oficiální aplikace a ovladače AMD"),
            ("🔵 Intel Graphics", "Ovladače pro Intel ARC / Iris Xe"),
            ("🔄 Windows Update", "Spustit vyhledání aktualizací systému"),
        ],

        "service_title": "Servis a reklamace",
        "service_text": "Rychlé odkazy pro servis, reklamaci nebo bezpečné odeslání počítače.",
        "service_tiles": [
            ("🧾 Reklamace", "Informace k reklamaci zboží"),
            ("🛠️ Servis počítače", "Pomoc s opravou nebo údržbou"),
            ("📦 Bezpečné odeslání PC", "Jak správně zabalit počítač"),
        ],

        "already_installed_title": "{name} je již nainstalovaný",
        "already_installed_text": "Aplikace {name} je už v počítači nainstalovaná.",
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
        "header_subtitle": "Rýchly štart, odporúčané aplikácie, podpora a servis na jednom mieste.",
        "footer": f"HelloComp.cz © 2026  |  verzia {APP_VERSION}",
        "footer_social_title": "Sledujte nás",
        "recommended_badge": "Odporúčané pre tento PC",

        "settings": "Nastavenia",
        "settings_title": "Nastavenia aplikácie",
        "settings_subtitle": "Jazyk, tapeta, aktualizácie a základné informácie.",
        "settings_language": "Jazyk aplikácie",
        "settings_wallpaper": "Tapeta HelloComp",
        "settings_wallpaper_text": "Nastaví pripravenú HelloComp tapetu na plochu Windows.",
        "settings_wallpaper_button": "Nastaviť tapetu",
        "settings_update": "Aktualizácia aplikácie",
        "settings_update_text": "Skontroluje, či je dostupná novšia verzia aplikácie HelloComp Start.",
        "settings_update_button": "Vyhľadať aktualizáciu aplikácie",
        "settings_about": "O aplikácii",
        "settings_about_text": f"Oficiálna aplikácia HelloComp Start. Verzia {APP_VERSION}.",

        "update_check_title": "Aktualizácia aplikácie",
        "update_checking": "Kontrolujem dostupnosť novej verzie…",
        "update_latest_title": "Aplikácia je aktuálna",
        "update_latest_text": f"Používate najnovšiu verziu aplikácie HelloComp Start ({APP_VERSION}).",
        "update_available_title": "Je dostupná nová verzia",
        "update_available_text": "Je dostupná nová verzia aplikácie HelloComp Start.\n\nAktuálna verzia: {current}\nNová verzia: {latest}\n\nChcete ju stiahnuť a nainštalovať?",
        "update_download_title": "Sťahujem aktualizáciu",
        "update_download_text": "Nová verzia sa stiahne a aplikácia sa potom automaticky reštartuje.",
        "update_error_title": "Aktualizácia sa nepodarila",
        "update_error_text": "Aktualizáciu sa nepodarilo overiť alebo stiahnuť.\n\nChyba:\n{error}",
        "update_dev_title": "Automatická aktualizácia",
        "update_dev_text": "Automatické prepísanie aplikácie funguje iba vo Windows .exe verzii.\n\nTeraz otvorím stránku na stiahnutie novej verzie.",

        "settings_wallpaper_success_title": "Tapeta nastavená",
        "settings_wallpaper_success_text": "Tapeta HelloComp bola nastavená.",
        "settings_wallpaper_missing_title": "Tapeta nenájdená",
        "settings_wallpaper_missing_text": "Súbor assets/HelloCompwallpaper.png nebol nájdený.",
        "settings_wallpaper_windows_only_title": "Tapeta",
        "settings_wallpaper_windows_only_text": "Automatické nastavenie tapety je dostupné vo Windows verzii aplikácie.",

        "wrong_driver_title": "Tento ovládač nie je odporúčaný",
        "wrong_driver_text": "Aplikácia detegovala grafickú kartu {detected}. Pre tento počítač je odporúčaný ovládač {recommended}.\n\nChcete aj napriek tomu otvoriť stránku {selected}?",
        "gpu_unknown_title": "Grafická karta nebola jednoznačne rozpoznaná",
        "gpu_unknown_text": "Aplikácia nedokázala jednoznačne určiť výrobcu grafickej karty. Otvorte iba ovládač, ktorý zodpovedá vašej grafickej karte.",

        "menu": ["Môj počítač", "Prvé kroky", "Podpora", "Aplikácie", "Servis"],

        "my_pc_title": "Môj počítač",
        "my_pc_text": "Prehľad hlavných parametrov zostavy. Detailné hardvérové údaje sa načítajú automaticky vo Windows.",
        "my_pc_refresh": "Načítať znova",
        "my_pc_loading": "Načítavam…",
        "my_pc_windows_only": "Detailné informácie sa automaticky načítajú vo Windows verzii aplikácie.",

        "pc_fields": {
            "manufacturer": "Výrobca",
            "cpu": "Procesor",
            "gpu": "Grafická karta",
            "ram": "Operačná pamäť",
            "drives": "Disky",
            "baseboard": "Základná doska",
        },

        "first_steps_title": "Prvé kroky",
        "first_steps_text": "Odporúčané kroky po prvom spustení počítača.",
        "first_steps_tiles": [
            ("📘 Návod na používanie", "Základné informácie po prvom spustení"),
            ("🪟 Aktivácia Windows", "Overenie aktivácie systému Windows"),
            ("⚙️ Odporúčané nastavenia", "Tipy pre stabilnú prevádzku"),
        ],

        "support_title": "Podpora HelloComp",
        "support_text": "Rýchla pomoc, kontakt a odpovede na najčastejšie otázky.",
        "support_tiles": [
            ("☎️ Kontakt", "Otvoriť kontaktnú stránku HelloComp"),
            ("✉️ Napísať e-mail", "info@hellocomp.cz"),
            ("❔ Časté otázky", "FAQ a odpovede na bežné otázky"),
        ],

        "software_title": "Odporúčané aplikácie",
        "software_text": "Aplikácie na hranie, komunikáciu, ovládače, správu počítača a základný test stability.",
        "software_tiles": [
            ("🎮 Steam", "Stiahnuť a spustiť inštalátor"),
            ("💬 Discord", "Stiahnuť a spustiť inštalátor"),
            ("🕹️ Epic Games", "Otvoriť stránku na stiahnutie"),
            ("🧪 OCCT", "Test stability CPU, GPU, RAM a zdroja"),
            ("🟢 nVidia App", "Oficiálna aplikácia a ovládače nVidia"),
            ("🔴 AMD Adrenalin", "Oficiálna aplikácia a ovládače AMD"),
            ("🔵 Intel Graphics", "Ovládače pre Intel ARC / Iris Xe"),
            ("🔄 Windows Update", "Spustiť vyhľadanie aktualizácií systému"),
        ],

        "service_title": "Servis a reklamácie",
        "service_text": "Rýchle odkazy pre servis, reklamáciu alebo bezpečné odoslanie počítača.",
        "service_tiles": [
            ("🧾 Reklamácie", "Informácie k reklamácii tovaru"),
            ("🛠️ Servis počítača", "Pomoc s opravou alebo údržbou"),
            ("📦 Bezpečné odoslanie PC", "Ako správne zabaliť počítač"),
        ],

        "already_installed_title": "{name} je už nainštalovaný",
        "already_installed_text": "Aplikácia {name} je už v počítači nainštalovaná.",
        "install_title": "Inštalovať {name}",
        "install_question": "Aplikácia stiahne oficiálny inštalátor {name} a spustí ho.\n\nPokračovať?",
        "download_title": "Sťahujem {name}",
        "download_text": "Inštalátor {name} sa sťahuje.\nPo dokončení sa automaticky spustí.",
        "install_error_title": "Inštalácia {name}",
        "install_error_text": "Inštalátor sa nepodarilo stiahnuť alebo spustiť.\n\nOtvorím oficiálnu stránku na stiahnutie.\n\nChyba:\n{error}",
    },
}


TRANSLATIONS["hu"] = {
    **TRANSLATIONS["cz"],
    "lang_label": "HU",
    "footer": f"HelloComp.cz © 2026  |  verzió {APP_VERSION}",
    "header_title": "Saját HelloComp számítógépem",
    "header_subtitle": "Gyors kezdés, ajánlott alkalmazások, támogatás és szerviz egy helyen.",
    "settings": "Beállítások",
    "settings_title": "Alkalmazás beállításai",
    "settings_subtitle": "Nyelv, háttérkép, frissítések és alapinformációk.",
    "settings_language": "Alkalmazás nyelve",
    "settings_wallpaper_button": "Háttérkép beállítása",
    "settings_update_button": "Alkalmazásfrissítés keresése",
    "menu": ["Saját gépem", "Első lépések", "Támogatás", "Alkalmazások", "Szerviz"],
    "my_pc_title": "Saját gépem",
    "support_title": "HelloComp támogatás",
    "software_title": "Ajánlott alkalmazások",
    "service_title": "Szerviz és reklamáció",
}

TRANSLATIONS["en"] = {
    **TRANSLATIONS["cz"],
    "lang_label": "EN",
    "footer": f"HelloComp.cz © 2026  |  version {APP_VERSION}",
    "header_title": "My HelloComp Computer",
    "header_subtitle": "Quick start, recommended apps, support and service in one place.",
    "settings": "Settings",
    "settings_title": "Application settings",
    "settings_subtitle": "Language, wallpaper, updates and basic information.",
    "settings_language": "Application language",
    "settings_wallpaper": "HelloComp wallpaper",
    "settings_wallpaper_text": "Sets the prepared HelloComp wallpaper on the Windows desktop.",
    "settings_wallpaper_button": "Set wallpaper",
    "settings_update": "Application update",
    "settings_update_text": "Checks whether a newer version of HelloComp Start is available.",
    "settings_update_button": "Check for application update",
    "settings_about": "About app",
    "settings_about_text": f"Official HelloComp Start application. Version {APP_VERSION}.",
    "update_check_title": "Application update",
    "update_checking": "Checking for a new version…",
    "update_latest_title": "Application is up to date",
    "update_latest_text": f"You are using the latest version of HelloComp Start ({APP_VERSION}).",
    "update_available_title": "New version available",
    "update_available_text": "A new version of HelloComp Start is available.\n\nCurrent version: {current}\nNew version: {latest}\n\nDo you want to download and install it?",
    "update_download_title": "Downloading update",
    "update_download_text": "The new version will be downloaded and the app will restart automatically.",
    "update_error_title": "Update failed",
    "update_error_text": "The update could not be checked or downloaded.\n\nError:\n{error}",
    "update_dev_title": "Automatic update",
    "update_dev_text": "Automatic replacement works only in the Windows .exe version.\n\nThe download page will now open.",
    "settings_wallpaper_success_title": "Wallpaper set",
    "settings_wallpaper_success_text": "HelloComp wallpaper has been set.",
    "settings_wallpaper_missing_title": "Wallpaper not found",
    "settings_wallpaper_missing_text": "File assets/HelloCompwallpaper.png was not found.",
    "settings_wallpaper_windows_only_title": "Wallpaper",
    "settings_wallpaper_windows_only_text": "Automatic wallpaper setup is available in the Windows version of the app.",
    "recommended_badge": "Recommended for this PC",
    "menu": ["My PC", "First steps", "Support", "Apps", "Service"],
    "my_pc_title": "My PC",
    "my_pc_text": "Overview of the main PC parameters. Detailed hardware information is loaded automatically on Windows.",
    "my_pc_refresh": "Reload",
    "my_pc_loading": "Loading…",
    "my_pc_windows_only": "Detailed information is loaded automatically in the Windows version of the app.",
    "pc_fields": {
        "manufacturer": "Manufacturer",
        "cpu": "Processor",
        "gpu": "Graphics card",
        "ram": "Memory",
        "drives": "Drives",
        "baseboard": "Motherboard",
    },
    "first_steps_title": "First steps",
    "first_steps_text": "Recommended steps after the first computer start.",
    "support_title": "HelloComp support",
    "support_text": "Quick help, contact and answers to frequently asked questions.",
    "software_title": "Recommended apps",
    "software_text": "Apps for gaming, communication, drivers, PC management and basic stability testing.",
    "service_title": "Service and warranty",
    "service_text": "Quick links for service, warranty claim or safe PC shipping.",
}

TRANSLATIONS["ua"] = {
    **TRANSLATIONS["en"],
    "lang_label": "UA",
    "footer": f"HelloComp.cz © 2026  |  версія {APP_VERSION}",
    "header_title": "Мій комп’ютер HelloComp",
    "header_subtitle": "Швидкий старт, рекомендовані програми, підтримка та сервіс в одному місці.",
    "settings": "Налаштування",
    "settings_title": "Налаштування програми",
    "settings_language": "Мова програми",
    "settings_wallpaper_button": "Встановити шпалери",
    "settings_update_button": "Перевірити оновлення програми",
    "menu": ["Мій ПК", "Перші кроки", "Підтримка", "Програми", "Сервіс"],
    "my_pc_title": "Мій ПК",
    "support_title": "Підтримка HelloComp",
    "software_title": "Рекомендовані програми",
    "service_title": "Сервіс",
}


LANGUAGE_URLS = {
    "cz": {
        "contact": "https://www.hellocomp.cz/kontakt/",
        "faq": "https://www.hellocomp.cz/casto-kladene-otazky--faq/",
        "home": "https://www.hellocomp.cz/",
    },
    "sk": {
        "contact": "https://www.hellocomp.cz/sk/kontakt/",
        "faq": "https://www.hellocomp.cz/sk/casto-kladene-otazky--faq/",
        "home": "https://www.hellocomp.cz/sk/",
    },
    "hu": {
        "contact": "https://www.hellocomp.cz/hu/kapcsolat/",
        "faq": "https://www.hellocomp.cz/hu/gyakran-ismetelt-kerdesek--gyik/",
        "home": "https://www.hellocomp.cz/hu/",
    },
    "en": {
        "contact": "https://www.hellocomp.cz/kontakt/",
        "faq": "https://www.hellocomp.cz/casto-kladene-otazky--faq/",
        "home": "https://www.hellocomp.cz/",
    },
    "ua": {
        "contact": "https://www.hellocomp.cz/kontakt/",
        "faq": "https://www.hellocomp.cz/casto-kladene-otazky--faq/",
        "home": "https://www.hellocomp.cz/",
    },
}


def load_settings():
    try:
        if SETTINGS_FILE.exists():
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

    return {}


def save_settings(settings):
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as error:
        print(f"⚠️ Nastavení se nepodařilo uložit: {error}")


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

    print("⚠️ Font nenalezen nebo se nepodařil načíst.")
    return "Arial"


def load_font_family_from_candidates(paths, label):
    font_path = find_first_existing(paths)

    if not font_path:
        print(f"⚠️ {label} font nenalezen.")
        return None

    font_id = QFontDatabase.addApplicationFont(str(font_path))

    if font_id == -1:
        print(f"⚠️ {label} font existuje, ale nepodařilo se ho načíst: {font_path}")
        return None

    families = QFontDatabase.applicationFontFamilies(font_id)

    if not families:
        print(f"⚠️ {label} font nemá dostupnou family: {font_path}")
        return None

    print(f"✅ {label} font načten: {font_path}")
    print(f"✅ {label} font family: {families[0]}")
    return families[0]


def find_logo():
    logo_path = find_first_existing(LOGO_CANDIDATES)

    if logo_path:
        print(f"✅ Logo nalezeno: {logo_path}")
        return logo_path

    print("⚠️ Logo nenalezeno.")
    return None


def open_url(url):
    if url:
        webbrowser.open(url)


def version_to_tuple(version):
    version = str(version).strip().lower()
    numbers = [int(x) for x in re.findall(r"\d+", version)]

    while len(numbers) < 4:
        numbers.append(0)

    return tuple(numbers[:4])


def is_newer_version(latest, current):
    return version_to_tuple(latest) > version_to_tuple(current)


def fetch_update_manifest():
    request = urllib.request.Request(
        VERSION_MANIFEST_URL,
        headers={
            "User-Agent": f"HelloCompStart/{APP_VERSION}",
            "Cache-Control": "no-cache",
        },
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read().decode("utf-8")

    return json.loads(raw)


def download_file(url, target_path):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"HelloCompStart/{APP_VERSION}"}
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        data = response.read()

    if not data:
        raise RuntimeError("Stažený soubor je prázdný.")

    target_path.write_bytes(data)


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

    t = TRANSLATIONS.get(language, TRANSLATIONS["cz"])

    return {
        "manufacturer": "HelloComp",
        "cpu": platform.processor() or platform.machine() or "—",
        "gpu": t["my_pc_windows_only"],
        "ram": t["my_pc_windows_only"],
        "drives": t["my_pc_windows_only"],
        "baseboard": t["my_pc_windows_only"],
    }


def detect_gpu_vendor_from_info(info):
    gpu_text = str(info.get("gpu", "")).lower()

    if "nvidia" in gpu_text or "geforce" in gpu_text or "quadro" in gpu_text or "rtx" in gpu_text or "gtx" in gpu_text:
        return "nvidia"

    if "amd" in gpu_text or "radeon" in gpu_text or "rx " in gpu_text:
        return "amd"

    if "intel" in gpu_text or "arc" in gpu_text or "iris" in gpu_text:
        return "intel"

    return None


def find_windows_executable(exe_name):
    if not is_windows():
        return None

    search_roots = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
        os.environ.get("APPDATA"),
    ]

    for root in search_roots:
        if not root:
            continue

        root_path = Path(root)

        try:
            matches = list(root_path.rglob(exe_name))
            if matches:
                return str(matches[0])
        except Exception:
            pass

    return None


def check_installed_app(installer_key):
    if installer_key == "steam":
        return find_windows_executable("steam.exe")

    if installer_key == "discord":
        discord = find_windows_executable("Discord.exe")
        if discord:
            return discord
        return find_windows_executable("Update.exe")

    return None


def download_and_run_installer(parent, installer_key, language):
    t = TRANSLATIONS.get(language, TRANSLATIONS["cz"])
    installer = SOFTWARE_INSTALLERS.get(installer_key)

    if not installer:
        return

    name = installer["name"]

    if not is_windows():
        webbrowser.open(installer["fallback_url"])
        return

    installed_path = check_installed_app(installer_key)

    if installed_path:
        QMessageBox.information(
            parent,
            t["already_installed_title"].format(name=name),
            t["already_installed_text"].format(name=name)
        )
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
            headers={"User-Agent": f"Mozilla/5.0 HelloCompStart/{APP_VERSION}"}
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


class AppBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()

        base = QLinearGradient(0, 0, rect.width(), rect.height())
        base.setColorAt(0.00, QColor("#0F1118"))
        base.setColorAt(0.52, QColor("#18243C"))
        base.setColorAt(1.00, QColor("#284C87"))
        painter.fillRect(rect, base)

        soft = QLinearGradient(0, 0, rect.width(), 0)
        soft.setColorAt(0.00, QColor(255, 255, 255, 0))
        soft.setColorAt(0.72, QColor(0, 114, 198, 10))
        soft.setColorAt(1.00, QColor(0, 114, 198, 26))
        painter.fillRect(rect, soft)

        painter.end()


class SvgLogo(QLabel):
    def __init__(self, svg_path, width=360, height=76, scale_factor=0.64, right_padding=4, y_offset=-3):
        super().__init__()
        self.svg_path = str(svg_path)
        self.scale_factor = scale_factor
        self.right_padding = right_padding
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

            x = self.width() - target_width - self.right_padding
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
        self.setFixedHeight(34)
        self.setCheckable(True)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        rect = QRectF(3.0, 3.0, self.width() - 6.0, self.height() - 6.0)

        if self.isChecked():
            gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
            gradient.setColorAt(0.0, QColor("#1f4f8f"))
            gradient.setColorAt(1.0, QColor("#0072c6"))

            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(rect, 8, 8)

            text_color = QColor("#ffffff")

        elif self.underMouse():
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 12))
            painter.drawRoundedRect(rect, 8, 8)

            text_color = QColor(255, 255, 255, 220)

        else:
            text_color = QColor(255, 255, 255, 166)

        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

        painter.end()


class LangButton(QPushButton):
    def __init__(self, text, language):
        super().__init__(text)
        self.language = language
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setFixedHeight(31)
        self.setFixedWidth(74)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.isChecked():
            bg = QColor(255, 255, 255, 40)
            border = QColor(255, 255, 255, 88)
            text_color = QColor(255, 255, 255, 245)
        elif self.underMouse():
            bg = QColor(255, 255, 255, 27)
            border = QColor(255, 255, 255, 58)
            text_color = QColor(255, 255, 255, 225)
        else:
            bg = QColor(255, 255, 255, 15)
            border = QColor(255, 255, 255, 34)
            text_color = QColor(255, 255, 255, 185)

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

        elif self.language == "en":
            painter.setBrush(QColor("#012169"))
            painter.drawRect(x, y, w, h)
            painter.setBrush(QColor("#ffffff"))
            painter.drawRect(x, y + 5, w, 2)
            painter.drawRect(x + 8, y, 2, h)
            painter.setBrush(QColor("#c8102e"))
            painter.drawRect(x, y + 5, w, 1)
            painter.drawRect(x + 8, y, 1, h)

        elif self.language == "ua":
            painter.setBrush(QColor("#0057b7"))
            painter.drawRect(x, y, w, h // 2)
            painter.setBrush(QColor("#ffd700"))
            painter.drawRect(x, y + h // 2, w, h - h // 2)


class SettingsButton(QPushButton):
    def __init__(self):
        super().__init__("⚙")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(38, 31)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.isChecked():
            bg = QColor(255, 255, 255, 44)
            border = QColor(255, 255, 255, 92)
        elif self.underMouse():
            bg = QColor(255, 255, 255, 28)
            border = QColor(255, 255, 255, 60)
        else:
            bg = QColor(255, 255, 255, 16)
            border = QColor(255, 255, 255, 34)

        painter.setPen(QPen(border, 1))
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 9, 9)

        painter.setPen(QColor("#ffffff"))
        font = QFont(self.font())
        font.setPixelSize(17)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self.text())

        painter.end()


class SocialButton(QPushButton):
    ICONS = {
        "facebook": "\uf39e",
        "instagram": "\uf16d",
        "discord": "\uf392",
    }

    FALLBACK_ICONS = {
        "facebook": "f",
        "instagram": "◎",
        "discord": "D",
    }

    def __init__(self, text, social_type, icon_font_family=None):
        super().__init__(text)
        self.social_type = social_type
        self.icon_font_family = icon_font_family
        self.setObjectName("FooterSocialButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(31)
        self.setFixedWidth(104)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.underMouse():
            bg = QColor("#ffffff")
            border = QColor(36, 79, 136, 70)
            icon_bg = QColor("#244f88")
            icon_color = QColor("#ffffff")
            text_color = QColor("#244f88")
        else:
            bg = QColor(255, 255, 255, 214)
            border = QColor(36, 79, 136, 32)
            icon_bg = QColor(36, 79, 136, 18)
            icon_color = QColor("#244f88")
            text_color = QColor("#244f88")

        painter.setPen(QPen(border, 1))
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 9, 9)

        icon_rect = QRectF(8, 5, 21, 21)

        painter.setPen(Qt.NoPen)
        painter.setBrush(icon_bg)
        painter.drawRoundedRect(icon_rect, 7, 7)

        painter.setPen(icon_color)

        if self.icon_font_family:
            icon_font = QFont(self.icon_font_family)
            icon_font.setPixelSize(11)
            icon_font.setWeight(QFont.Normal)
            painter.setFont(icon_font)
            painter.drawText(icon_rect, Qt.AlignCenter, self.ICONS.get(self.social_type, ""))
        else:
            fallback_font = QFont(self.font())
            fallback_font.setBold(True)
            fallback_font.setPixelSize(11)
            painter.setFont(fallback_font)
            painter.drawText(icon_rect, Qt.AlignCenter, self.FALLBACK_ICONS.get(self.social_type, ""))

        text_font = QFont(self.font())
        text_font.setBold(False)
        text_font.setPixelSize(12)
        painter.setFont(text_font)
        painter.setPen(text_color)

        painter.drawText(
            QRectF(37, 0, self.width() - 41, self.height()),
            Qt.AlignVCenter | Qt.AlignLeft,
            self.text()
        )

        painter.end()


class TileButton(QPushButton):
    def __init__(
        self,
        title,
        subtitle,
        url=None,
        installer_key=None,
        language="cz",
        tile_key=None,
        driver_vendor=None,
    ):
        super().__init__()
        self.url = url
        self.installer_key = installer_key
        self.language = language
        self.tile_key = tile_key
        self.driver_vendor = driver_vendor
        self.base_title = title
        self.base_subtitle = subtitle
        self.is_recommended = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(86)
        self.update_text(title, subtitle)
        self.clicked.connect(self.handle_click)

    def update_text(self, title, subtitle, badge=None):
        self.base_title = title
        self.base_subtitle = subtitle

        if badge:
            self.setText(f"{title}\n{badge}\n{subtitle}")
            self.setProperty("recommended", True)
            self.is_recommended = True
        else:
            self.setText(f"{title}\n{subtitle}")
            self.setProperty("recommended", False)
            self.is_recommended = False

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_language(self, language):
        self.language = language

    def handle_click(self):
        window = self.window()

        if self.url == "windows_update" and hasattr(window, "open_windows_update"):
            window.open_windows_update()
            return

        if self.driver_vendor and hasattr(window, "should_open_driver"):
            if not window.should_open_driver(self.driver_vendor):
                return

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
        self.setMinimumHeight(82)
        self.setMaximumHeight(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 11, 16, 11)
        layout.setSpacing(6)

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

        self.settings = load_settings()
        self.language = self.settings.get("language", "cz")

        if self.language not in TRANSLATIONS:
            self.language = "cz"

        self.pc_info = {}
        self.gpu_vendor = None

        self.app_font = load_app_font()
        self.fa_brands_font = load_font_family_from_candidates(FA_BRANDS_CANDIDATES, "Font Awesome Brands")
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

        self.main_background = AppBackground()

        main_layout = QVBoxLayout(self.main_background)
        main_layout.setContentsMargins(36, 28, 36, 22)
        main_layout.setSpacing(0)

        header = self.create_header()
        menu_wrap = self.create_menu_wrap()

        self.pages = QStackedWidget()
        self.pages.setObjectName("Pages")
        self.pages.addWidget(self.create_my_pc_page())
        self.pages.addWidget(self.create_first_steps_page())
        self.pages.addWidget(self.create_support_page())
        self.pages.addWidget(self.create_software_page())
        self.pages.addWidget(self.create_service_page())
        self.pages.addWidget(self.create_settings_page())

        main_layout.addWidget(header)
        main_layout.addWidget(menu_wrap)
        main_layout.addWidget(self.pages)

        self.footer = self.create_footer()

        root.addWidget(self.main_background)
        root.addWidget(self.footer)

        self.set_active_menu(0)
        self.apply_styles()
        self.update_language(self.language)
        self.load_pc_information()

        QTimer.singleShot(1800, self.check_for_updates_silent)

    def create_header(self):
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(140)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(34, 18, 34, 18)
        layout.setSpacing(28)

        left_widget = QWidget()
        left_widget.setObjectName("HeaderTextWrapper")

        left = QVBoxLayout(left_widget)
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(8)

        self.header_title = QLabel()
        self.header_title.setObjectName("HeaderTitle")

        self.header_subtitle = QLabel()
        self.header_subtitle.setObjectName("HeaderSubtitle")
        self.header_subtitle.setWordWrap(True)
        self.header_subtitle.setMaximumWidth(570)

        left.addStretch()
        left.addWidget(self.header_title)
        left.addWidget(self.header_subtitle)
        left.addStretch()

        right_widget = QWidget()
        right_widget.setObjectName("HeaderRightWrapper")
        right_widget.setFixedWidth(440)

        right = QVBoxLayout(right_widget)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(10)

        settings_row = QWidget()
        settings_row.setObjectName("LangRow")

        settings_layout = QHBoxLayout(settings_row)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(7)
        settings_layout.addStretch()

        self.settings_button = SettingsButton()
        self.settings_button.clicked.connect(lambda: self.set_active_menu(5))
        settings_layout.addWidget(self.settings_button)

        logo_holder = QWidget()
        logo_holder.setObjectName("LogoHolder")
        logo_holder.setFixedSize(410, 76)

        logo_layout = QVBoxLayout(logo_holder)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        if self.logo_path and self.logo_path.suffix.lower() == ".svg":
            logo = SvgLogo(
                self.logo_path,
                width=390,
                height=76,
                scale_factor=0.64,
                right_padding=2,
                y_offset=-3
            )
            logo_layout.addWidget(logo, alignment=Qt.AlignCenter)

        elif self.logo_path and self.logo_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            logo = QLabel()
            logo.setObjectName("LogoImage")
            pixmap = QPixmap(str(self.logo_path))
            logo.setPixmap(pixmap.scaled(390, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            logo_layout.addWidget(logo, alignment=Qt.AlignRight)

        else:
            logo = QLabel("HELLOCOMP")
            logo.setObjectName("LogoFallback")
            logo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            logo_layout.addWidget(logo)

        right.addWidget(settings_row)
        right.addWidget(logo_holder, alignment=Qt.AlignRight)

        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 0)

        return header

    def create_footer(self):
        footer = QFrame()
        footer.setObjectName("Footer")
        footer.setFixedHeight(60)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(42, 0, 42, 0)
        footer_layout.setSpacing(14)

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
        footer_social_layout.setSpacing(7)

        self.footer_facebook = SocialButton("Facebook", "facebook", self.fa_brands_font)
        self.footer_facebook.clicked.connect(lambda: open_url("https://www.facebook.com/HelloComp.cz"))

        self.footer_instagram = SocialButton("Instagram", "instagram", self.fa_brands_font)
        self.footer_instagram.clicked.connect(lambda: open_url("https://www.instagram.com/hellocompcz"))

        self.footer_discord = SocialButton("Discord", "discord", self.fa_brands_font)
        self.footer_discord.clicked.connect(lambda: open_url("https://discord.com/invite/dQDDXyek9x"))

        footer_social_layout.addWidget(self.footer_facebook)
        footer_social_layout.addWidget(self.footer_instagram)
        footer_social_layout.addWidget(self.footer_discord)

        footer_layout.addWidget(self.footer_text)
        footer_layout.addStretch()
        footer_layout.addWidget(self.footer_social_title)
        footer_layout.addWidget(self.footer_social)

        return footer

    def create_menu_wrap(self):
        wrap = QWidget()
        wrap.setObjectName("MenuWrap")
        wrap.setFixedHeight(76)

        wrap_layout = QHBoxLayout(wrap)
        wrap_layout.setContentsMargins(0, 17, 0, 17)
        wrap_layout.setSpacing(0)

        menu = QFrame()
        menu.setObjectName("Menu")
        menu.setFixedHeight(42)
        menu.setFixedWidth(830)

        layout = QHBoxLayout(menu)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.setSpacing(5)

        for index in range(5):
            btn = MenuButton()
            btn.clicked.connect(lambda checked=False, i=index: self.set_active_menu(i))
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        wrap_layout.addStretch()
        wrap_layout.addWidget(menu)
        wrap_layout.addStretch()

        return wrap

    def set_active_menu(self, index):
        self.pages.setCurrentIndex(index)

        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

        if hasattr(self, "settings_button"):
            self.settings_button.setChecked(index == 5)

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
        self.refresh_pc_button.setFixedHeight(36)
        self.refresh_pc_button.clicked.connect(self.load_pc_information_with_feedback)

        top_layout.addStretch()
        top_layout.addWidget(self.refresh_pc_button)

        grid_wrapper = QWidget()
        grid_wrapper.setObjectName("PcGridWrapper")

        grid = QGridLayout(grid_wrapper)
        grid.setContentsMargins(0, 12, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(11)

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
            ("home", None, "first_guide", None),
            ("home", None, "activation", None),
            ("home", None, "settings", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_support_page(self):
        page = self.create_page_base("support")
        tiles = self.create_tiles_row("support", [
            ("contact", None, "contact", None),
            ("mailto:info@hellocomp.cz", None, "email", None),
            ("faq", None, "faq", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_software_page(self):
        page = self.create_page_base("software")

        tiles = self.create_tiles_grid("software", [
            (None, "steam", "steam", None),
            (None, "discord", "discord", None),
            (SOFTWARE_URLS["epic"], None, "epic", None),
            (SOFTWARE_URLS["occt"], None, "occt", None),
            (SOFTWARE_URLS["nvidia"], None, "nvidia", "nvidia"),
            (SOFTWARE_URLS["amd"], None, "amd", "amd"),
            (SOFTWARE_URLS["intel"], None, "intel", "intel"),
            ("windows_update", None, "windows_update", None),
        ], columns=4)

        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_service_page(self):
        page = self.create_page_base("service")
        tiles = self.create_tiles_row("service", [
            ("home", None, "claim", None),
            ("contact", None, "service", None),
            ("faq", None, "shipping", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_settings_page(self):
        page = QWidget()
        page.setObjectName("Page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(13)

        title_label = QLabel()
        title_label.setObjectName("PageTitle")

        text_label = QLabel()
        text_label.setObjectName("PageText")
        text_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(text_label)

        self.page_labels["settings_page"] = {
            "title": title_label,
            "text": text_label,
        }

        settings_grid = QGridLayout()
        settings_grid.setContentsMargins(0, 18, 0, 0)
        settings_grid.setHorizontalSpacing(14)
        settings_grid.setVerticalSpacing(12)

        self.settings_language_title = QLabel()
        self.settings_language_title.setObjectName("SettingsSectionTitle")

        language_box = QFrame()
        language_box.setObjectName("SettingsCard")

        language_layout = QVBoxLayout(language_box)
        language_layout.setContentsMargins(16, 14, 16, 14)
        language_layout.setSpacing(12)
        language_layout.addWidget(self.settings_language_title)

        lang_row = QWidget()
        lang_row_layout = QHBoxLayout(lang_row)
        lang_row_layout.setContentsMargins(0, 0, 0, 0)
        lang_row_layout.setSpacing(8)

        self.settings_lang_buttons = []

        for language in ["cz", "sk", "hu", "en", "ua"]:
            btn = LangButton(TRANSLATIONS[language]["lang_label"], language)
            btn.clicked.connect(lambda checked=False, lang=language: self.update_language(lang))
            self.settings_lang_buttons.append(btn)
            lang_row_layout.addWidget(btn)

        lang_row_layout.addStretch()
        language_layout.addWidget(lang_row)

        self.settings_wallpaper_title = QLabel()
        self.settings_wallpaper_title.setObjectName("SettingsSectionTitle")

        self.settings_wallpaper_text = QLabel()
        self.settings_wallpaper_text.setObjectName("SettingsText")
        self.settings_wallpaper_text.setWordWrap(True)

        self.settings_wallpaper_button = QPushButton()
        self.settings_wallpaper_button.setObjectName("SettingsActionButton")
        self.settings_wallpaper_button.setCursor(Qt.PointingHandCursor)
        self.settings_wallpaper_button.setFixedHeight(36)
        self.settings_wallpaper_button.clicked.connect(self.set_hellocomp_wallpaper)

        wallpaper_box = QFrame()
        wallpaper_box.setObjectName("SettingsCard")

        wallpaper_layout = QVBoxLayout(wallpaper_box)
        wallpaper_layout.setContentsMargins(16, 14, 16, 14)
        wallpaper_layout.setSpacing(10)
        wallpaper_layout.addWidget(self.settings_wallpaper_title)
        wallpaper_layout.addWidget(self.settings_wallpaper_text)
        wallpaper_layout.addWidget(self.settings_wallpaper_button, alignment=Qt.AlignLeft)

        self.settings_update_title = QLabel()
        self.settings_update_title.setObjectName("SettingsSectionTitle")

        self.settings_update_text = QLabel()
        self.settings_update_text.setObjectName("SettingsText")
        self.settings_update_text.setWordWrap(True)

        self.settings_update_button = QPushButton()
        self.settings_update_button.setObjectName("SettingsActionButton")
        self.settings_update_button.setCursor(Qt.PointingHandCursor)
        self.settings_update_button.setFixedHeight(36)
        self.settings_update_button.clicked.connect(self.check_for_updates_manual)

        update_box = QFrame()
        update_box.setObjectName("SettingsCard")

        update_layout = QVBoxLayout(update_box)
        update_layout.setContentsMargins(16, 14, 16, 14)
        update_layout.setSpacing(10)
        update_layout.addWidget(self.settings_update_title)
        update_layout.addWidget(self.settings_update_text)
        update_layout.addWidget(self.settings_update_button, alignment=Qt.AlignLeft)

        self.settings_about_title = QLabel()
        self.settings_about_title.setObjectName("SettingsSectionTitle")

        self.settings_about_text = QLabel()
        self.settings_about_text.setObjectName("SettingsText")
        self.settings_about_text.setWordWrap(True)

        about_box = QFrame()
        about_box.setObjectName("SettingsCard")

        about_layout = QVBoxLayout(about_box)
        about_layout.setContentsMargins(16, 14, 16, 14)
        about_layout.setSpacing(10)
        about_layout.addWidget(self.settings_about_title)
        about_layout.addWidget(self.settings_about_text)

        settings_grid.addWidget(language_box, 0, 0, 1, 2)
        settings_grid.addWidget(wallpaper_box, 1, 0)
        settings_grid.addWidget(update_box, 1, 1)
        settings_grid.addWidget(about_box, 2, 0, 1, 2)

        layout.addLayout(settings_grid)
        layout.addStretch()

        return page

    def create_page_base(self, key):
        page = QWidget()
        page.setObjectName("Page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(13)

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
        layout.setContentsMargins(0, 18, 0, 0)
        layout.setSpacing(15)

        self.tile_groups[key] = []

        for url, installer_key, tile_key, driver_vendor in actions:
            tile = TileButton(
                "",
                "",
                url,
                installer_key,
                self.language,
                tile_key=tile_key,
                driver_vendor=driver_vendor,
            )
            self.tile_groups[key].append(tile)
            layout.addWidget(tile)

        return wrapper

    def create_tiles_grid(self, key, actions, columns=4):
        wrapper = QWidget()
        wrapper.setObjectName("TilesWrapper")

        layout = QGridLayout(wrapper)
        layout.setContentsMargins(0, 18, 0, 0)
        layout.setHorizontalSpacing(13)
        layout.setVerticalSpacing(12)

        self.tile_groups[key] = []

        for index, (url, installer_key, tile_key, driver_vendor) in enumerate(actions):
            tile = TileButton(
                "",
                "",
                url,
                installer_key,
                self.language,
                tile_key=tile_key,
                driver_vendor=driver_vendor,
            )
            self.tile_groups[key].append(tile)

            row = index // columns
            column = index % columns

            layout.addWidget(tile, row, column)

        return wrapper

    def resolve_url(self, url_key_or_url):
        if not url_key_or_url:
            return None

        if url_key_or_url == "windows_update":
            return "windows_update"

        if url_key_or_url.startswith("http") or url_key_or_url.startswith("mailto:"):
            return url_key_or_url

        return LANGUAGE_URLS.get(self.language, LANGUAGE_URLS["cz"]).get(url_key_or_url)

    def update_tile_urls(self):
        mapped_tiles = {
            "first_steps": ["home", "home", "home"],
            "support": ["contact", "mailto:info@hellocomp.cz", "faq"],
            "service": ["home", "contact", "faq"],
        }

        for group_key, url_keys in mapped_tiles.items():
            tiles = self.tile_groups.get(group_key, [])

            for tile, url_key in zip(tiles, url_keys):
                tile.url = self.resolve_url(url_key)

        software_urls = {
            "steam": None,
            "discord": None,
            "epic": SOFTWARE_URLS["epic"],
            "occt": SOFTWARE_URLS["occt"],
            "nvidia": SOFTWARE_URLS["nvidia"],
            "amd": SOFTWARE_URLS["amd"],
            "intel": SOFTWARE_URLS["intel"],
            "windows_update": "windows_update",
        }

        for tile in self.tile_groups.get("software", []):
            if tile.tile_key in software_urls:
                tile.url = software_urls[tile.tile_key]

    def should_open_driver(self, selected_vendor):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])

        if self.gpu_vendor is None:
            QMessageBox.information(
                self,
                t["gpu_unknown_title"],
                t["gpu_unknown_text"]
            )
            return True

        if self.gpu_vendor == selected_vendor:
            return True

        detected_name = DRIVER_NAMES.get(self.gpu_vendor, self.gpu_vendor)
        recommended_name = DRIVER_NAMES.get(self.gpu_vendor, self.gpu_vendor)
        selected_name = DRIVER_NAMES.get(selected_vendor, selected_vendor)

        reply = QMessageBox.warning(
            self,
            t["wrong_driver_title"],
            t["wrong_driver_text"].format(
                detected=detected_name,
                recommended=recommended_name,
                selected=selected_name,
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return reply == QMessageBox.Yes

    def apply_gpu_recommendations(self):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])
        recommended_tile = None

        if self.gpu_vendor == "nvidia":
            recommended_tile = "nvidia"

        elif self.gpu_vendor == "amd":
            recommended_tile = "amd"

        elif self.gpu_vendor == "intel":
            recommended_tile = "intel"

        tiles = self.tile_groups.get("software", [])

        for tile in tiles:
            badge = t["recommended_badge"] if tile.tile_key == recommended_tile else None
            tile.update_text(tile.base_title, tile.base_subtitle, badge=badge)

    def open_windows_update(self):
        if is_windows():
            try:
                subprocess.Popen(
                    ["UsoClient.exe", "StartScan"],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

            try:
                os.startfile("ms-settings:windowsupdate-action")
                return
            except Exception:
                pass

            try:
                os.startfile("ms-settings:windowsupdate")
                return
            except Exception:
                pass

        webbrowser.open("https://support.microsoft.com/windows")

    def set_hellocomp_wallpaper(self):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])

        if not WALLPAPER_FILE.exists():
            QMessageBox.warning(
                self,
                t["settings_wallpaper_missing_title"],
                t["settings_wallpaper_missing_text"]
            )
            return

        if not is_windows():
            QMessageBox.information(
                self,
                t["settings_wallpaper_windows_only_title"],
                t["settings_wallpaper_windows_only_text"]
            )
            return

        try:
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2

            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                str(WALLPAPER_FILE),
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )

            QMessageBox.information(
                self,
                t["settings_wallpaper_success_title"],
                t["settings_wallpaper_success_text"]
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                t["settings_wallpaper_missing_title"],
                str(error)
            )

    def check_for_updates_manual(self):
        self.check_for_updates(manual=True)

    def check_for_updates_silent(self):
        self.check_for_updates(manual=False)

    def check_for_updates(self, manual=False):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])

        if manual:
            self.settings_update_button.setEnabled(False)
            self.settings_update_button.setText(t["update_checking"])
            QApplication.processEvents()

        try:
            manifest = fetch_update_manifest()
            latest_version = str(manifest.get("version", "")).strip()
            exe_url = str(manifest.get("windows_exe_url", "")).strip()
            release_url = str(manifest.get("release_url", GITHUB_RELEASES_URL)).strip()

            if not latest_version:
                raise RuntimeError("Manifest neobsahuje položku version.")

            if not is_newer_version(latest_version, APP_VERSION):
                if manual:
                    QMessageBox.information(
                        self,
                        t["update_latest_title"],
                        t["update_latest_text"]
                    )
                return

            reply = QMessageBox.question(
                self,
                t["update_available_title"],
                t["update_available_text"].format(
                    current=APP_VERSION,
                    latest=latest_version,
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply != QMessageBox.Yes:
                return

            if not is_windows() or not is_frozen_exe():
                QMessageBox.information(
                    self,
                    t["update_dev_title"],
                    t["update_dev_text"]
                )
                open_url(release_url or GITHUB_RELEASES_URL)
                return

            if not exe_url:
                raise RuntimeError("Manifest neobsahuje položku windows_exe_url.")

            self.download_and_install_update(exe_url, latest_version)

        except Exception as error:
            if manual:
                QMessageBox.warning(
                    self,
                    t["update_error_title"],
                    t["update_error_text"].format(error=error)
                )

        finally:
            if manual:
                self.settings_update_button.setEnabled(True)
                self.settings_update_button.setText(t["settings_update_button"])

    def download_and_install_update(self, exe_url, latest_version):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])

        QMessageBox.information(
            self,
            t["update_download_title"],
            t["update_download_text"]
        )

        temp_dir = Path(tempfile.gettempdir()) / "HelloCompStartUpdate"
        temp_dir.mkdir(parents=True, exist_ok=True)

        new_exe = temp_dir / f"HelloComp_Start_{latest_version}.exe"
        updater_bat = temp_dir / "update_hellocomp_start.bat"

        current_exe = Path(sys.executable).resolve()

        download_file(exe_url, new_exe)

        if not new_exe.exists() or new_exe.stat().st_size < 1024 * 1024:
            raise RuntimeError("Stažená aktualizace je příliš malá nebo poškozená.")

        bat_content = f"""@echo off
setlocal
set "OLD_EXE={current_exe}"
set "NEW_EXE={new_exe}"

timeout /t 2 /nobreak >nul

:copyloop
copy /Y "%NEW_EXE%" "%OLD_EXE%" >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto copyloop
)

start "" "%OLD_EXE%"

timeout /t 2 /nobreak >nul
del "%NEW_EXE%" >nul 2>nul
del "%~f0" >nul 2>nul
endlocal
"""

        updater_bat.write_text(bat_content, encoding="utf-8")

        subprocess.Popen(
            ["cmd", "/c", str(updater_bat)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, "CREATE_NEW_CONSOLE") else 0,
        )

        QApplication.quit()

    def load_pc_information_with_feedback(self):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])
        original_text = t["my_pc_refresh"]

        self.refresh_pc_button.setEnabled(False)
        self.refresh_pc_button.setText(t["my_pc_loading"])
        QApplication.processEvents()

        self.load_pc_information()

        QTimer.singleShot(450, lambda: self.finish_refresh_button(original_text))

    def finish_refresh_button(self, text):
        self.refresh_pc_button.setText(text)
        self.refresh_pc_button.setEnabled(True)

    def load_pc_information(self):
        t = TRANSLATIONS.get(self.language, TRANSLATIONS["cz"])

        try:
            info = get_pc_info(self.language)
        except Exception as error:
            info = {key: "—" for key in t["pc_fields"].keys()}
            info["manufacturer"] = "HelloComp"
            info["cpu"] = str(error)

        self.pc_info = info
        self.gpu_vendor = detect_gpu_vendor_from_info(info)

        for key, card in self.pc_cards.items():
            title = t["pc_fields"].get(key, key)
            value = info.get(key, "—")
            card.update_card(title, value)

        self.apply_gpu_recommendations()

    def update_language(self, language):
        if language not in TRANSLATIONS:
            language = "cz"

        self.language = language
        self.settings["language"] = language
        save_settings(self.settings)

        t = TRANSLATIONS.get(language, TRANSLATIONS["cz"])

        self.setWindowTitle(t["window_title"])
        self.header_title.setText(t["header_title"])
        self.header_subtitle.setText(t["header_subtitle"])
        self.footer_text.setText(t["footer"])
        self.footer_social_title.setText(t["footer_social_title"])
        self.refresh_pc_button.setText(t["my_pc_refresh"])

        for index, text in enumerate(t["menu"]):
            self.menu_buttons[index].setText(text)

        if hasattr(self, "settings_lang_buttons"):
            for btn in self.settings_lang_buttons:
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

        self.page_labels["settings_page"]["title"].setText(t["settings_title"])
        self.page_labels["settings_page"]["text"].setText(t["settings_subtitle"])

        self.settings_language_title.setText(t["settings_language"])
        self.settings_wallpaper_title.setText(t["settings_wallpaper"])
        self.settings_wallpaper_text.setText(t["settings_wallpaper_text"])
        self.settings_wallpaper_button.setText(t["settings_wallpaper_button"])

        self.settings_update_title.setText(t["settings_update"])
        self.settings_update_text.setText(t["settings_update_text"])
        self.settings_update_button.setText(t["settings_update_button"])

        self.settings_about_title.setText(t["settings_about"])
        self.settings_about_text.setText(t["settings_about_text"])

        for key, card in self.pc_cards.items():
            card.title_label.setText(t["pc_fields"].get(key, key))

        self.update_tile_urls()
        self.apply_gpu_recommendations()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                color: #ffffff;
                font-family: "{self.app_font}";
                font-size: 15px;
            }}

            #Header {{
                background: rgba(15, 17, 24, 0.34);
                border: 1px solid rgba(255,255,255,0.045);
                border-radius: 18px;
            }}

            #HeaderTextWrapper,
            #HeaderRightWrapper,
            #LangRow,
            #LogoHolder,
            #PcTopRow,
            #PcGridWrapper,
            #FooterSocial,
            #Pages,
            #MenuWrap {{
                background: transparent;
            }}

            #HeaderTitle {{
                background: transparent;
                font-size: 30px;
                font-weight: 400;
                color: #ffffff;
                letter-spacing: 0.2px;
            }}

            #HeaderSubtitle {{
                background: transparent;
                font-size: 15px;
                font-weight: 400;
                color: rgba(255,255,255,0.72);
                line-height: 1.45;
            }}

            #LogoImage {{
                background: transparent;
                border: none;
            }}

            #LogoFallback {{
                background: transparent;
                color: #ffffff;
                font-size: 27px;
                font-weight: 400;
                letter-spacing: 5px;
            }}

            #Menu {{
                background: rgba(8, 15, 27, 0.58);
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 14px;
            }}

            QPushButton {{
                border: none;
                color: #ffffff;
                font-weight: 400;
            }}

            MenuButton {{
                background: transparent;
                border: none;
                color: transparent;
                padding: 0;
                margin: 0;
                font-size: 14px;
                font-weight: 400;
            }}

            LangButton {{
                background: transparent;
                border: none;
                color: transparent;
            }}

            #Page {{
                background: rgba(15,17,24,0.12);
                border: 1px solid rgba(255,255,255,0.035);
                border-radius: 18px;
            }}

            #PageTitle {{
                background: transparent;
                font-size: 30px;
                font-weight: 400;
                color: #ffffff;
                letter-spacing: 0.2px;
            }}

            #PageText {{
                background: transparent;
                font-size: 15px;
                font-weight: 400;
                color: rgba(255,255,255,0.72);
            }}

            #TilesWrapper {{
                background: transparent;
            }}

            TileButton {{
                background: rgba(255,255,255,0.056);
                border: 1px solid rgba(255,255,255,0.065);
                border-radius: 14px;
                padding: 15px;
                text-align: left;
                font-size: 12px;
                font-weight: 400;
                line-height: 1.28;
                color: #ffffff;
            }}

            TileButton:hover {{
                background: rgba(255,255,255,0.092);
                border: 1px solid rgba(255,255,255,0.12);
            }}

            TileButton[recommended="true"] {{
                background: rgba(0, 114, 198, 0.19);
                border: 1px solid rgba(0, 114, 198, 0.34);
            }}

            TileButton[recommended="true"]:hover {{
                background: rgba(0, 114, 198, 0.25);
                border: 1px solid rgba(0, 114, 198, 0.45);
            }}

            #PcInfoCard,
            #SettingsCard {{
                background: rgba(255,255,255,0.052);
                border: 1px solid rgba(255,255,255,0.065);
                border-radius: 13px;
            }}

            #PcInfoTitle,
            #SettingsSectionTitle {{
                background: transparent;
                color: rgba(255,255,255,0.56);
                font-size: 12px;
                font-weight: 400;
                letter-spacing: 0.025em;
            }}

            #PcInfoValue,
            #SettingsText {{
                background: transparent;
                color: #ffffff;
                font-size: 12px;
                font-weight: 400;
                line-height: 1.25;
            }}

            #RefreshPcButton,
            #SettingsActionButton {{
                background: rgba(255,255,255,0.09);
                border: 1px solid rgba(255,255,255,0.13);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 13px;
            }}

            #RefreshPcButton:hover,
            #SettingsActionButton:hover {{
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.20);
            }}

            #RefreshPcButton:disabled,
            #SettingsActionButton:disabled {{
                background: rgba(255,255,255,0.055);
                border: 1px solid rgba(255,255,255,0.09);
                color: rgba(255,255,255,0.58);
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
                font-size: 12px;
                font-weight: 400;
            }}

            #FooterSocialTitle {{
                background: transparent;
                color: #5f6f82;
                font-size: 12px;
                font-weight: 400;
                letter-spacing: 0.02em;
            }}

            #FooterSocialButton {{
                background: transparent;
                border: none;
                color: #244f88;
                font-size: 12px;
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