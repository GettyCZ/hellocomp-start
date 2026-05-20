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


def download_and_run_installer(parent, installer_key):
    installer = SOFTWARE_INSTALLERS.get(installer_key)

    if not installer:
        QMessageBox.warning(parent, "Instalace", "Instalátor nebyl nalezen.")
        return

    name = installer["name"]

    if not is_windows():
        QMessageBox.information(
            parent,
            "Instalace",
            f"Přímá instalace je dostupná ve Windows.\n\nNa tomto systému otevřu stránku pro stažení: {name}."
        )
        webbrowser.open(installer["fallback_url"])
        return

    reply = QMessageBox.question(
        parent,
        f"Instalovat {name}",
        f"Aplikace stáhne oficiální instalátor {name} a spustí ho.\n\nPokračovat?",
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
            f"Stahuji {name}",
            f"Instalátor {name} se začne stahovat.\nPo dokončení se automaticky spustí."
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
            f"Instalace {name}",
            f"Instalátor se nepodařilo stáhnout nebo spustit.\n\nOtevřu oficiální stránku pro stažení.\n\nChyba:\n{error}"
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
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(64)
        self.setCheckable(True)


class TileButton(QPushButton):
    def __init__(self, title, subtitle, url=None, installer_key=None):
        super().__init__()
        self.url = url
        self.installer_key = installer_key
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(128)
        self.setText(f"{title}\n{subtitle}")
        self.clicked.connect(self.handle_click)

    def handle_click(self):
        if self.installer_key:
            download_and_run_installer(self.window(), self.installer_key)
            return

        if self.url:
            webbrowser.open(self.url)


class HelloCompStart(QWidget):
    def __init__(self):
        super().__init__()

        self.app_font = load_app_font()
        self.logo_path = find_logo()

        self.setWindowTitle("HelloComp Start")
        self.resize(1180, 720)
        self.setMinimumSize(980, 620)

        if APP_ICON.exists():
            self.setWindowIcon(QIcon(str(APP_ICON)))

        self.menu_buttons = []

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

        footer = QLabel("HelloComp.cz © 2026  |  verze 1.0")
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFixedHeight(42)

        root.addWidget(header)
        root.addWidget(menu)
        root.addWidget(self.pages)
        root.addWidget(footer)

        self.set_active_menu(0)
        self.apply_styles()

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

        title = QLabel("Můj počítač HelloComp")
        title.setObjectName("HeaderTitle")

        subtitle = QLabel("První spuštění, podpora, servis a doporučený software")
        subtitle.setObjectName("HeaderSubtitle")

        left_wrapper.addStretch()
        left_wrapper.addWidget(title)
        left_wrapper.addWidget(subtitle)
        left_wrapper.addStretch()

        logo_wrapper = QFrame()
        logo_wrapper.setObjectName("LogoWrapper")
        logo_wrapper.setFixedSize(330, 88)

        logo_layout = QVBoxLayout(logo_wrapper)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        if self.logo_path and self.logo_path.suffix.lower() == ".svg":
            logo = SvgLogo(self.logo_path, width=300, height=78)
            logo_layout.addWidget(logo, alignment=Qt.AlignCenter)

        elif self.logo_path and self.logo_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            logo = QLabel()
            logo.setObjectName("LogoImage")

            pixmap = QPixmap(str(self.logo_path))
            logo.setPixmap(
                pixmap.scaled(
                    300,
                    78,
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

        layout.addWidget(left_wrapper_widget)
        layout.addStretch()
        layout.addWidget(logo_wrapper)

        return header

    def create_menu(self):
        menu = QFrame()
        menu.setObjectName("Menu")
        menu.setFixedHeight(64)

        layout = QHBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        items = [
            "První kroky",
            "Potřebuji podporu",
            "Volitelný software",
            "Potřebuji servis",
            "Staňte se fanouškem",
        ]

        for index, text in enumerate(items):
            btn = MenuButton(text)
            btn.clicked.connect(lambda checked=False, i=index: self.set_active_menu(i))
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        return menu

    def set_active_menu(self, index):
        self.pages.setCurrentIndex(index)

        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

    def create_first_steps_page(self):
        page = self.create_page_base(
            "První kroky s novým počítačem",
            "Pro váš nový počítač jsme připravili základní návody a doporučení."
        )

        tiles = self.create_tiles_row([
            (
                "Návod k použití počítače",
                "Základní informace po prvním spuštění",
                "https://www.hellocomp.cz/",
                None
            ),
            (
                "Aktivace Windows",
                "Jak ověřit aktivaci systému Windows",
                "https://www.hellocomp.cz/",
                None
            ),
            (
                "Doporučené nastavení",
                "Tipy pro stabilní a plynulý provoz",
                "https://www.hellocomp.cz/",
                None
            ),
        ])

        page.layout().addWidget(tiles)
        page.layout().addStretch()

        return page

    def create_support_page(self):
        page = self.create_page_base(
            "Potřebuji podporu",
            "Jsme tu pro vás, pokud potřebujete poradit s počítačem, objednávkou nebo nastavením."
        )

        tiles = self.create_tiles_row([
            (
                "Kontaktovat podporu",
                "Otevřít kontaktní stránku HelloComp",
                "https://www.hellocomp.cz/kontakty/",
                None
            ),
            (
                "Napsat e-mail",
                "Rychlý kontakt na podporu",
                "mailto:info@hellocomp.cz",
                None
            ),
            (
                "Časté otázky",
                "Odpovědi na běžné dotazy",
                "https://www.hellocomp.cz/",
                None
            ),
        ])

        page.layout().addWidget(tiles)
        page.layout().addStretch()

        return page

    def create_software_page(self):
        page = self.create_page_base(
            "Volitelný software",
            "Vyberte si software, který se vám může hodit pro hraní, práci i správu počítače."
        )

        tiles = self.create_tiles_row([
            (
                "Instalovat Steam",
                "Stáhnout a spustit oficiální instalátor",
                None,
                "steam"
            ),
            (
                "Instalovat Discord",
                "Stáhnout a spustit oficiální instalátor",
                None,
                "discord"
            ),
            (
                "NVIDIA App",
                "Ovladače a nástroje pro nVidia grafiky",
                "https://www.nvidia.com/",
                None
            ),
            (
                "AMD Adrenalin",
                "Ovladače a nástroje pro AMD grafiky",
                "https://www.amd.com/",
                None
            ),
            (
                "Epic Games Launcher",
                "Otevřít oficiální stránku pro stažení",
                "https://store.epicgames.com/download",
                None
            ),
        ])

        page.layout().addWidget(tiles)
        page.layout().addStretch()

        return page

    def create_service_page(self):
        page = self.create_page_base(
            "Servis a reklamace",
            "Potřebujete servis, údržbu nebo řešit reklamaci? Tady najdete potřebné odkazy."
        )

        tiles = self.create_tiles_row([
            (
                "Reklamace",
                "Informace k reklamaci zboží",
                "https://www.hellocomp.cz/",
                None
            ),
            (
                "Servis počítače",
                "Pomoc s opravou nebo údržbou",
                "https://www.hellocomp.cz/",
                None
            ),
            (
                "Bezpečné odeslání PC",
                "Jak správně zabalit počítač",
                "https://www.hellocomp.cz/",
                None
            ),
        ])

        page.layout().addWidget(tiles)
        page.layout().addStretch()

        return page

    def create_fans_page(self):
        page = self.create_page_base(
            "Staňte se fanouškem HelloComp",
            "Sledujte nás, přidejte se do komunity nebo nám zanechte hodnocení."
        )

        tiles = self.create_tiles_row([
            (
                "Discord",
                "Připojit se ke komunitě",
                "https://discord.com/",
                None
            ),
            (
                "Instagram",
                "Sledovat novinky a sestavy",
                "https://www.instagram.com/",
                None
            ),
            (
                "Facebook",
                "Sledovat HelloComp",
                "https://www.facebook.com/",
                None
            ),
            (
                "Hodnocení",
                "Pomozte nám zpětnou vazbou",
                "https://www.hellocomp.cz/",
                None
            ),
        ])

        page.layout().addWidget(tiles)
        page.layout().addStretch()

        return page

    def create_page_base(self, title, text):
        page = QWidget()
        page.setObjectName("Page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 30)
        layout.setSpacing(26)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")

        text_label = QLabel(text)
        text_label.setObjectName("PageText")
        text_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(text_label)

        return page

    def create_tiles_row(self, items):
        wrapper = QWidget()
        wrapper.setObjectName("TilesWrapper")

        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(22)

        for title, subtitle, url, installer_key in items:
            tile = TileButton(title, subtitle, url, installer_key)
            layout.addWidget(tile)

        return wrapper

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

            #HeaderTextWrapper {{
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

            MenuButton:checked:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #18243C,
                    stop:1 #284C87
                );
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

    if APP_ICON.exists():
        app.setWindowIcon(QIcon(str(APP_ICON)))

    window = HelloCompStart()
    window.show()

    sys.exit(app.exec())