import os
import configparser
import subprocess
import json
from loguru import logger
from gi.repository import Gtk, Gdk


class KDEColorManager:
    # Default window size
    DEFAULT_WINDOW_WIDTH = 800
    DEFAULT_WINDOW_HEIGHT = 600

    def __init__(self):
        self.colors = self.get_colors()
        logger.info(f"Loaded KDE colors: {self.colors}")

    def get_colors_from_dbus(self):
        try:
            cmd = [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                "var c = theme.colors; JSON.stringify({selection: c.selection})",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout.strip())
                logger.info(f"Got colors from DBus: {data}")
                return data
        except Exception as e:
            logger.error(f"Failed to get colors from DBus: {e}")
        return None

    def get_colors(self):
        colors = {}
        kdeglobals = os.path.expanduser("~/.config/kdeglobals")

        if os.path.exists(kdeglobals):
            config = configparser.ConfigParser()
            config.read(kdeglobals)

            # Get accent color from Colors:Button section
            if "Colors:Button" in config:
                accent = config["Colors:Button"].get("DecorationFocus", "")
                if accent:
                    r, g, b = map(int, accent.split(","))
                    colors["accent_color"] = f"#{r:02x}{g:02x}{b:02x}"

            # Get colors from Colors:Window
            if "Colors:Window" in config:
                bg = config["Colors:Window"].get("BackgroundNormal", "")
                fg = config["Colors:Window"].get("ForegroundNormal", "")

                if bg:
                    r, g, b = map(int, bg.split(","))
                    colors["window_background"] = f"#{r:02x}{g:02x}{b:02x}"
                if fg:
                    r, g, b = map(int, fg.split(","))
                    colors["window_foreground"] = f"#{r:02x}{g:02x}{b:02x}"

            # Get colors from Colors:Button
            if "Colors:Button" in config:
                bg = config["Colors:Button"].get("BackgroundNormal", "")
                fg = config["Colors:Button"].get("ForegroundNormal", "")

                if bg:
                    r, g, b = map(int, bg.split(","))
                    colors["button_background"] = f"#{r:02x}{g:02x}{b:02x}"
                if fg:
                    r, g, b = map(int, fg.split(","))
                    colors["button_foreground"] = f"#{r:02x}{g:02x}{b:02x}"

        # Default colors if not found
        defaults = {
            "window_background": "#282828",
            "window_foreground": "#dfdfdf",
            "button_background": "#4d4d4d",
            "button_foreground": "#dfdfdf",
            "accent_color": "#b8544c",
        }

        for key, value in defaults.items():
            if key not in colors:
                colors[key] = value

        return colors

    def get_css(self):
        accent_color = self.colors.get("accent_color", "#b8544c")

        return f"""
window {{
    background-color: {self.colors['window_background']};
    color: {self.colors['window_foreground']};
    min-width: {self.DEFAULT_WINDOW_WIDTH}px;
    min-height: {self.DEFAULT_WINDOW_HEIGHT}px;
}}

/* Базовые стили для кликабельных элементов */
button {{
    cursor: pointer;
}}

.clickable {{
    cursor: pointer;
}}

.header {{
    background-color: {self.colors['window_background']};
    padding: 8px;
    border-bottom: 1px solid alpha({self.colors['window_foreground']}, 0.1);
}}

.page-title {{
    font-weight: bold;
    font-size: 1.2em;
    margin-right: 16px;
    color: {self.colors['window_foreground']};
}}

.network-id {{
    color: alpha({self.colors['window_foreground']}, 0.7);
    font-size: 0.9em;
}}

.list-row-buttons {{
    margin-left: 12px;
    spacing: 8px;
}}

.list-row-buttons button {{
    padding: 4px 12px;  /* Уменьшаем отступы */
    min-height: 28px;   /* Уменьшаем минимальную высоту */
    font-size: 0.9em;   /* Уменьшаем размер шрифта */
}}

window button,
button.text-button,
button.image-button {{
    all: unset;
    background-color: {self.colors['button_background']};
    color: {self.colors['button_foreground']};
    padding: 8px 16px;
    margin: 0 4px;
    border-radius: 4px;
    min-height: 34px;
    min-width: 34px;
    transition: all 200ms ease;
    box-shadow: none;
    -gtk-icon-shadow: none;
    text-shadow: none;
    outline: none;
    cursor: pointer !important;
}}

window button:hover,
button.text-button:hover,
button.image-button:hover {{
    background-color: {accent_color};
    color: white;
}}

window button:active,
button.text-button:active,
button.image-button:active {{
    filter: brightness(80%);
}}

/* Стиль для пустого состояния (empty state) */
.empty-state {{
    cursor: pointer !important;
    transition: all 200ms ease;
}}

.empty-state:hover {{
    background-color: alpha({self.colors['button_background']}, 0.1);
    border-radius: 8px;
}}

list {{
    background-color: {self.colors['window_background']};
    color: {self.colors['window_foreground']};
}}

.list-row-box {{
    padding: 12px;
    border-bottom: 1px solid alpha({self.colors['window_foreground']}, 0.1);
    min-height: 64px;
}}

.list-row-info {{
    margin-right: 12px;
    min-height: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.sidebar {{
    background-color: {self.colors['window_background']};
    padding: 12px;
    border-right: 1px solid alpha({self.colors['window_foreground']}, 0.1);
}}

.user-id-label {{
    color: alpha({self.colors['window_foreground']}, 0.7);
    font-size: 0.9em;
}}

.you-label {{
    color: {accent_color};
    font-weight: bold;
    font-size: 0.9em;
    margin-top: 2px;
}}

/* Стили для владельца сети */
.network-owner {{
    color: {accent_color};
    font-weight: bold;
}}

.network-owner-icon {{
    color: {accent_color};
    margin-left: 8px;
}}

.members-box {{
    margin: 12px;
    padding: 12px;
    background-color: alpha({self.colors['window_background']}, 0.5);
    border-radius: 4px;
}}

.members-list {{
    margin-top: 8px;
}}

.dialog-content {{
    background-color: alpha({self.colors['window_background']}, 0.6);
    border: 1px solid alpha({self.colors['window_foreground']}, 0.1);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 24px;
    min-width: min(400px, 80%);
}}

.dialog-content label {{
    margin-top: 4px;
    margin-bottom: 4px;
}}

.dialog-text-area {{
    background-color: alpha({self.colors['button_background']}, 0.3);
    border-radius: 4px;
    padding: 8px;
    margin-top: 8px;
    margin-bottom: 8px;
}}

.dialog-button {{
    padding: 8px 24px;
    margin-top: 8px;
    min-width: 100px;
}}
"""

    def apply_to_window(self, window):
        css_provider = Gtk.CssProvider()
        css = self.get_css()
        logger.debug(f"Applying CSS:\n{css}")
        css_provider.load_from_data(css.encode())

        display = window.get_display()
        logger.debug(f"Display: {display}")

        Gtk.StyleContext.add_provider_for_display(
            display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        logger.debug("CSS provider added to display")
