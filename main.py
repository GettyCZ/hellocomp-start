import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QFontDatabase, QPixmap, QPainter, QIcon
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
)


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
    },
    "discord": {
        "name": "Discord",
        "url": "https://discord.com/api/download?platform=win",
        "filename": "DiscordSetup.exe",
        "fallback_url": "https://discord.com/download",
    },
}


TRANSLATIONS = {
    "cz": {
        "lang_label": "🇨🇿 CZ",
        "window_title": "HelloComp Start",
        "header_title": "Můj počítač HelloComp",
        "header_subtitle": "První spuštění, podpora, servis a doporučený software",
        "footer": "HelloComp.cz © 2026  |  verze 1.0",

        "menu": [
            "První kroky",
            "Potřebuji podporu",
            "Volitelný software",
            "Potřebuji servis",
            "Staňte se fanouškem",
        ],

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

        "fans_title": "Staňte se fanouškem HelloComp",
        "fans_text": "Sledujte nás, přidejte se do komunity nebo nám zanechte hodnocení.",
        "fans_tiles": [
            ("Discord", "Připojit se ke komunitě"),
            ("Instagram", "Sledovat novinky a sestavy"),
            ("Facebook", "Sledovat HelloComp"),
            ("Hodnocení", "Pomozte nám zpětnou vazbou"),
        ],

        "install_only_windows": "Přímá instalace je dostupná ve Windows.\n\nNa tomto systému otevřu stránku pro stažení: {name}.",
        "installer_missing": "Instalátor nebyl nalezen.",
        "install_title": "Instalovat {name}",
        "install_question": "Aplikace stáhne oficiální instalátor {name} a spustí ho.\n\nPokračovat?",
        "download_title": "Stahuji {name}",
        "download_text": "Instalátor {name} se začne stahovat.\nPo dokončení se automaticky spustí.",
        "install_error_title": "Instalace {name}",
        "install_error_text": "Instalátor se nepodařilo stáhnout nebo spustit.\n\nOtevřu oficiální stránku pro stažení.\n\nChyba:\n{error}",
    },

    "sk": {
        "lang_label": "🇸🇰 SK",
        "window_title": "HelloComp Start",
        "header_title": "Môj počítač HelloComp",
        "header_subtitle": "Prvé spustenie, podpora, servis a odporúčaný softvér",
        "footer": "HelloComp.cz © 2026  |  verzia 1.0",

        "menu": [
            "Prvé kroky",
            "Potrebujem podporu",
            "Voliteľný softvér",
            "Potrebujem servis",
            "Staňte sa fanúšikom",
        ],

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

        "fans_title": "Staňte sa fanúšikom HelloComp",
        "fans_text": "Sledujte nás, pridajte sa do komunity alebo nám zanechajte hodnotenie.",
        "fans_tiles": [
            ("Discord", "Pripojiť sa ku komunite"),
            ("Instagram", "Sledovať novinky a zostavy"),
            ("Facebook", "Sledovať HelloComp"),
            ("Hodnotenie", "Pomôžte nám spätnou väzbou"),
        ],

        "install_only_windows": "Priama inštalácia je dostupná vo Windows.\n\nNa tomto systéme otvorím stránku na stiahnutie: {name}.",
        "installer_missing": "Inštalátor nebol nájdený.",
        "install_title": "Inštalovať {name}",
        "install_question": "Aplikácia stiahne oficiálny inštalátor {name} a spustí ho.\n\nPokračovať?",
        "download_title": "Sťahujem {name}",
        "download_text": "Inštalátor {name} sa začne sťahovať.\nPo dokončení sa automaticky spustí.",
        "install_error_title": "Inštalácia {name}",
        "install_error_text": "Inštalátor sa nepodarilo stiahnuť alebo spustiť.\n\nOtvorím oficiálnu stránku na stiahnutie.\n\nChyba:\n{error}",
    },

    "hu": {
        "lang_label": "🇭🇺 HU",
        "window_title": "HelloComp Start",
        "header_title": "Saját HelloComp számítógépem",
        "header_subtitle": "Első indítás, támogatás, szerviz és ajánlott szoftverek",
        "footer": "HelloComp.cz © 2026  |  verzió 1.0",

        "menu": [
            "Első lépések",
            "Támogatásra van szükségem",
            "Választható szoftverek",
            "Szervizre van szükségem",
            "Legyen rajongónk",
        ],

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

        "fans_title": "Legyen a HelloComp rajongója",
        "fans_text": "Kövessen minket, csatlakozzon a közösséghez, vagy hagyjon értékelést.",
        "fans_tiles": [
            ("Discord", "Csatlakozás a közösséghez"),
            ("Instagram", "Újdonságok és gépösszeállítások követése"),
            ("Facebook", "HelloComp követése"),
            ("Értékelés", "Segítsen nekünk visszajelzéssel"),
        ],

        "install_only_windows": "A közvetlen telepítés Windows alatt érhető el.\n\nEzen a rendszeren megnyitom a letöltési oldalt: {name}.",
        "installer_missing": "A telepítő nem található.",
        "install_title": "{name} telepítése",
        "install_question": "Az alkalmazás letölti és elindítja a(z) {name} hivatalos telepítőjét.\n\nFolytatja?",
        "download_title": "{name} letöltése",
        "download_text": "A(z) {name} telepítője letöltésre kerül.\nA letöltés után automatikusan elindul.",
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


def download_and_run_installer(parent, installer_key, language):
    t = TRANSLATIONS[language]
    installer = SOFTWARE_INSTALLERS.get(installer_key)

    if not installer:
        QMessageBox.warning(parent, "Instalace", t["installer_missing"])
        return

    name = installer["name"]

    if not is_windows():
        QMessageBox.information(
            parent,
            t["install_title"].format(name=name),
            t["install_only_windows"].format(name=name)
        )
        webbrowser.open(installer["fallback_url"])
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
                "User-Agent": "Mozilla/5.0 HelloCompStart/1.0"
            }
        )

        QMessageBox.information(
            parent,
            t["download_title"].format(name=name),
            t["download_text"].format(name=name)
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()

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


class SvgLogo(QLabel):
    def __init__(self, svg_path, width=300, height=82):
        super().__init__()
        self.svg_path = str(svg_path)
        self.setObjectName("LogoImage")
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.render_svg()

    def render_svg(self):
        renderer = QSvgRenderer(self.svg_path)

        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(Qt.transparent)

        default_size = renderer.defaultSize()

        if default_size.width() <= 0 or default_size.height() <= 0:
            target = QRectF(0, 0, self.width(), self.height())
        else:
            scale = min(
                self.width() / default_size.width(),
                self.height() / default_size.height()
            )

            target_width = default_size.width() * scale
            target_height = default_size.height() * scale

            x = (self.width() - target_width) / 2
            y = (self.height() - target_height) / 2

            target = QRectF(x, y, target_width, target_height)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
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
        self.setFixedHeight(30)
        self.setMinimumWidth(62)


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


class HelloCompStart(QWidget):
    def __init__(self):
        super().__init__()

        self.language = "cz"
        self.app_font = load_app_font()
        self.logo_path = find_logo()

        self.setWindowTitle(TRANSLATIONS[self.language]["window_title"])
        self.resize(1180, 720)
        self.setMinimumSize(980, 620)

        if is_windows() and APP_ICON.exists():
            self.setWindowIcon(QIcon(str(APP_ICON)))

        self.menu_buttons = []
        self.lang_buttons = []
        self.page_labels = {}
        self.tile_groups = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = self.create_header()
        menu = self.create_menu()

        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_first_steps_page())
        self.pages.addWidget(self.create_support_page())
        self.pages.addWidget(self.create_software_page())
        self.pages.addWidget(self.create_service_page())
        self.pages.addWidget(self.create_fans_page())

        self.footer = QLabel()
        self.footer.setObjectName("Footer")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setFixedHeight(42)

        root.addWidget(header)
        root.addWidget(menu)
        root.addWidget(self.pages)
        root.addWidget(self.footer)

        self.set_active_menu(0)
        self.apply_styles()
        self.update_language("cz")

    def create_header(self):
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(118)

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
        right_layout.setContentsMargins(0, 10, 0, 10)
        right_layout.setSpacing(8)

        lang_row = QWidget()
        lang_row.setObjectName("LangRow")

        lang_layout = QHBoxLayout(lang_row)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(6)
        lang_layout.addStretch()

        for language in ["cz", "sk", "hu"]:
            btn = LangButton(TRANSLATIONS[language]["lang_label"], language)
            btn.clicked.connect(lambda checked=False, lang=language: self.update_language(lang))
            self.lang_buttons.append(btn)
            lang_layout.addWidget(btn)

        logo_wrapper = QFrame()
        logo_wrapper.setObjectName("LogoWrapper")
        logo_wrapper.setFixedSize(330, 74)

        logo_layout = QVBoxLayout(logo_wrapper)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        if self.logo_path and self.logo_path.suffix.lower() == ".svg":
            logo = SvgLogo(self.logo_path, width=300, height=68)
            logo_layout.addWidget(logo, alignment=Qt.AlignCenter)

        elif self.logo_path and self.logo_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            logo = QLabel()
            logo.setObjectName("LogoImage")

            pixmap = QPixmap(str(self.logo_path))
            logo.setPixmap(
                pixmap.scaled(
                    300,
                    68,
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

    def create_fans_page(self):
        page = self.create_page_base("fans")
        tiles = self.create_tiles_row("fans", [
            ("https://discord.com/invite/dQDDXyek9x", None),
            ("https://www.instagram.com/hellocompcz", None),
            ("https://www.facebook.com/HelloComp.cz", None),
            ("https://www.hellocomp.cz/", None),
        ])
        page.layout().addWidget(tiles)
        page.layout().addStretch()
        return page

    def create_page_base(self, key):
        page = QWidget()
        page.setObjectName("Page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 30)
        layout.setSpacing(26)

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

    def update_language(self, language):
        self.language = language
        t = TRANSLATIONS[language]

        self.setWindowTitle(t["window_title"])
        self.header_title.setText(t["header_title"])
        self.header_subtitle.setText(t["header_subtitle"])
        self.footer.setText(t["footer"])

        for index, text in enumerate(t["menu"]):
            self.menu_buttons[index].setText(text)

        for btn in self.lang_buttons:
            btn.setChecked(btn.language == language)

        page_keys = ["first_steps", "support", "software", "service", "fans"]

        for key in page_keys:
            self.page_labels[key]["title"].setText(t[f"{key}_title"])
            self.page_labels[key]["text"].setText(t[f"{key}_text"])

            tiles_texts = t[f"{key}_tiles"]
            tiles = self.tile_groups[key]

            for tile, (title, subtitle) in zip(tiles, tiles_texts):
                tile.update_text(title, subtitle)
                tile.set_language(language)

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
            #LangRow {{
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
                font-size: 15px;
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
                background: rgba(255,255,255,0.075);
                border: 1px solid rgba(255,255,255,0.13);
                border-radius: 8px;
                color: rgba(255,255,255,0.74);
                font-size: 12px;
                font-weight: 400;
            }}

            LangButton:hover {{
                background: rgba(255,255,255,0.13);
                color: #ffffff;
            }}

            LangButton:checked {{
                background: rgba(255,255,255,0.20);
                border: 1px solid rgba(255,255,255,0.36);
                color: #ffffff;
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

            #Footer {{
                background: #0b111d;
                color: rgba(255,255,255,0.58);
                font-size: 13px;
                font-weight: 400;
                border-top: 1px solid rgba(255,255,255,0.06);
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if is_windows() and APP_ICON.exists():
        app.setWindowIcon(QIcon(str(APP_ICON)))

    window = HelloCompStart()
    window.show()

    sys.exit(app.exec())