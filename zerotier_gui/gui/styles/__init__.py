import os
from gi.repository import Gtk, Gdk
from .kde_colors import KDEColorManager


def load_css(window):
    # Применяем цвета KDE
    kde_colors = KDEColorManager()
    kde_colors.apply_to_window(window)

    # Загружаем пользовательские стили
    css_provider = Gtk.CssProvider()

    # Получаем путь к файлу стилей
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_file = os.path.join(current_dir, "custom.css")

    # Загружаем стили из файла
    try:
        css_provider.load_from_path(css_file)
        # Применяем стили ко всему приложению
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
    except Exception as e:
        pass
