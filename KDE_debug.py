import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import os
import configparser
import subprocess
import re
import json

class KDEColorDebug:
    def __init__(self):
        self.colors = self.get_colors_from_system()
        
    def get_colors_from_system(self):
        """Попытка получить цвета из разных источников"""
        colors = {}
        
        # Попробуем несколько методов и объединим результаты
        colors.update(self.get_colors_from_kdeglobals())
        colors.update(self.get_colors_from_qdbus())
        colors.update(self.get_colors_from_plasma_theme())
        
        # Если цвета всё ещё не найдены, используем значения по умолчанию
        if not colors:
            print("Не удалось найти цвета KDE, использую значения по умолчанию")
            colors = {
                "window_background": "#232627",
                "window_foreground": "#fcfcfc",
                "button_background": "#31363b",
                "button_foreground": "#fcfcfc",
                "selection_background": "#3daee9",
                "selection_foreground": "#fcfcfc",
                "view_background": "#1d2023",
                "view_foreground": "#fcfcfc"
            }
        
        return colors
    
    def get_colors_from_kdeglobals(self):
        """Получить цвета из файла kdeglobals"""
        colors = {}
        kdeglobals = os.path.expanduser("~/.config/kdeglobals")
        
        if os.path.exists(kdeglobals):
            config = configparser.ConfigParser()
            config.read(kdeglobals)
            
            # Отладочная информация о секциях
            print(f"Секции в kdeglobals: {config.sections()}")
            
            # Получаем имя активной темы
            theme_name = "Unknown"
            if "General" in config and "ColorScheme" in config["General"]:
                theme_name = config["General"]["ColorScheme"]
                print(f"Активная тема KDE: {theme_name}")
            
            # Попытка получить цвета из разных секций
            color_sections = ["Colors:Window", "Colors:Button", "Colors:View", "Colors:Selection", "WM"]
            for section in color_sections:
                if section in config:
                    print(f"Найдена секция {section} с ключами: {list(config[section].keys())}")
                    for key, value in config[section].items():
                        colors[f"{section.lower().replace(':', '_')}_{key}"] = value
        
        # Преобразование цветов из формата r,g,b в hex
        formatted_colors = {}
        for key, value in colors.items():
            if "," in value:
                try:
                    r, g, b = map(int, value.split(","))
                    formatted_colors[key] = f"#{r:02x}{g:02x}{b:02x}"
                except Exception as e:
                    print(f"Ошибка при преобразовании цвета {key}={value}: {str(e)}")
            else:
                formatted_colors[key] = value
        
        # Маппинг специфичных ключей в общие
        color_mapping = {
            "colors_window_backgroundnormal": "window_background",
            "colors_window_foregroundnormal": "window_foreground",
            "colors_button_backgroundnormal": "button_background",
            "colors_button_foregroundnormal": "button_foreground",
            "colors_selection_backgroundnormal": "selection_background",
            "colors_selection_foregroundnormal": "selection_foreground",
            "colors_view_backgroundnormal": "view_background",
            "colors_view_foregroundnormal": "view_foreground"
        }
        
        result = {}
        for kde_key, common_key in color_mapping.items():
            if kde_key in formatted_colors:
                result[common_key] = formatted_colors[kde_key]
                
        print(f"Цвета из kdeglobals: {result}")
        return result
    
    def get_colors_from_qdbus(self):
        """Попытка получить цвета через DBus"""
        colors = {}
        try:
            # Попытка запросить цвета через qdbus
            cmd = ["qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", 
                   "var theme = plasma.theme; JSON.stringify({accent: theme.colors.selection, background: theme.colors.background, foreground: theme.colors.text})"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                try:
                    theme_data = json.loads(result.stdout.strip())
                    print(f"Данные темы из DBus: {theme_data}")
                    if "accent" in theme_data:
                        colors["selection_background"] = theme_data["accent"]
                    if "background" in theme_data:
                        colors["window_background"] = theme_data["background"]
                    if "foreground" in theme_data:
                        colors["window_foreground"] = theme_data["foreground"]
                except json.JSONDecodeError:
                    print(f"Не удалось декодировать JSON из DBus: {result.stdout}")
        except Exception as e:
            print(f"Ошибка при получении цветов через DBus: {str(e)}")
        
        return colors
    
    def get_colors_from_plasma_theme(self):
        """Попытка получить цвета из текущей темы Plasma"""
        colors = {}
        try:
            # Пытаемся найти файл текущей темы плазмы
            theme_paths = [
                os.path.expanduser("~/.local/share/plasma/desktoptheme"),
                "/usr/share/plasma/desktoptheme"
            ]
            
            # Получаем имя текущей темы
            theme_name = self.get_current_plasma_theme()
            
            for base_path in theme_paths:
                theme_path = os.path.join(base_path, theme_name, "colors")
                if os.path.exists(theme_path):
                    print(f"Найден файл цветов темы Plasma: {theme_path}")
                    # Чтение файла цветов
                    with open(theme_path, 'r') as f:
                        content = f.read()
                        # Попытка извлечь цвета с помощью регулярных выражений
                        bg_color = re.search(r'BackgroundNormal=([\d,]+)', content)
                        fg_color = re.search(r'ForegroundNormal=([\d,]+)', content)
                        select_bg = re.search(r'SelectionBackground=([\d,]+)', content)
                        
                        if bg_color:
                            r, g, b = map(int, bg_color.group(1).split(","))
                            colors["window_background"] = f"#{r:02x}{g:02x}{b:02x}"
                        if fg_color:
                            r, g, b = map(int, fg_color.group(1).split(","))
                            colors["window_foreground"] = f"#{r:02x}{g:02x}{b:02x}"
                        if select_bg:
                            r, g, b = map(int, select_bg.group(1).split(","))
                            colors["selection_background"] = f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            print(f"Ошибка при чтении файла темы Plasma: {str(e)}")
            
        return colors
    
    def get_current_plasma_theme(self):
        """Получить имя текущей темы Plasma"""
        try:
            cmd = ["kreadconfig5", "--file", "plasmarc", "--group", "Theme", "--key", "name"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                theme_name = result.stdout.strip()
                print(f"Текущая тема Plasma: {theme_name}")
                return theme_name
        except Exception as e:
            print(f"Ошибка при получении имени темы Plasma: {str(e)}")
        
        return "default"  # По умолчанию
    
    def dump_all_color_files(self):
        """Вывести список всех найденных файлов цветов и их содержимое"""
        # Поиск файлов цветов в системе
        color_files = []
        
        # Пользовательские цвета
        user_colors = os.path.expanduser("~/.local/share/color-schemes")
        if os.path.exists(user_colors):
            for file in os.listdir(user_colors):
                if file.endswith(".colors"):
                    color_files.append(os.path.join(user_colors, file))
        
        # Системные цвета
        system_colors = "/usr/share/color-schemes"
        if os.path.exists(system_colors):
            for file in os.listdir(system_colors):
                if file.endswith(".colors"):
                    color_files.append(os.path.join(system_colors, file))
        
        print(f"Найдено {len(color_files)} файлов цветов:")
        for file in color_files[:5]:  # Выводим только первые 5 для краткости
            print(f"- {file}")
            
        # Чтение kdeglobals для определения текущей темы
        kdeglobals = os.path.expanduser("~/.config/kdeglobals")
        if os.path.exists(kdeglobals):
            print("\nСодержимое kdeglobals:")
            with open(kdeglobals, "r") as f:
                for line in f.readlines()[:20]:  # Только первые 20 строк
                    print(line.strip())

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.gtk.Example")
        self.connect("activate", self.on_activate)
        self.window = None
        
    def on_activate(self, app):
        if not self.window:
            # Загружаем и выводим отладочную информацию о цветах
            self.kde_colors = KDEColorDebug()
            self.kde_colors.dump_all_color_files()
            
            # Создаем окно
            self.window = Gtk.ApplicationWindow(application=app)
            self.window.set_default_size(600, 400)
            self.window.set_title("GTK с цветами KDE Plasma (Отладка)")
            
            # Получаем цвета
            colors = self.kde_colors.colors
            
            # Создаем CSS-провайдер для применения стилей
            css_provider = Gtk.CssProvider()
            
            # Создаем CSS с цветами KDE
            css = f"""
            window {{
                background-color: {colors.get("window_background", "#232627")};
                color: {colors.get("window_foreground", "#fcfcfc")};
            }}
            
            button {{
                background-color: {colors.get("button_background", "#31363b")};
                color: {colors.get("button_foreground", "#fcfcfc")};
                border-radius: 4px;
                padding: 8px;
            }}
            
            button:hover {{
                background-color: lighter({colors.get("button_background", "#31363b")}, 1.2);
            }}
            
            button:active {{
                background-color: {colors.get("selection_background", "#3daee9")};
                color: {colors.get("selection_foreground", "#fcfcfc")};
            }}
            
            entry {{
                background-color: {colors.get("view_background", "#1d2023")};
                color: {colors.get("view_foreground", "#fcfcfc")};
                border-radius: 4px;
                padding: 8px;
            }}
            
            label {{
                color: {colors.get("window_foreground", "#fcfcfc")};
            }}
            """
            
            css_provider.load_from_data(css.encode())
            
            # Применяем CSS ко всему приложению
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
            # Создаем контейнер с явным фоном
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_margin_top(16)
            box.set_margin_bottom(16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            self.window.set_child(box)
            
            # Добавляем метку с информацией о текущих цветах
            label = Gtk.Label(label="Цвета KDE Plasma (отладка)")
            box.append(label)
            
            # Добавляем отладочную информацию о цветах
            colors_text = "Обнаруженные цвета:\n\n"
            for key, value in self.kde_colors.colors.items():
                colors_text += f"{key}: {value}\n"
            
            colors_label = Gtk.Label(label=colors_text)
            colors_label.set_xalign(0)  # Выравнивание по левому краю
            box.append(colors_label)
            
            # Добавляем кнопку для обновления цветов
            refresh_button = Gtk.Button(label="Обновить цвета")
            refresh_button.connect("clicked", self.on_refresh_clicked)
            box.append(refresh_button)
            
            # Добавляем образцы цветов
            self.add_color_samples(box)
            
        self.window.present()
    
    def add_color_samples(self, container):
        """Добавить образцы цветов"""
        colors = self.kde_colors.colors
        
        # Добавляем заголовок
        samples_label = Gtk.Label(label="Образцы цветов:")
        samples_label.set_margin_top(12)
        container.append(samples_label)
        
        # Создаем контейнер для образцов
        samples_grid = Gtk.Grid()
        samples_grid.set_column_spacing(8)
        samples_grid.set_row_spacing(8)
        container.append(samples_grid)
        
        # Определяем цвета для отображения
        color_samples = [
            ("Фон окна", colors.get("window_background", "#232627")),
            ("Текст окна", colors.get("window_foreground", "#fcfcfc")),
            ("Фон кнопки", colors.get("button_background", "#31363b")),
            ("Текст кнопки", colors.get("button_foreground", "#fcfcfc")),
            ("Фон выделения", colors.get("selection_background", "#3daee9")),
            ("Текст выделения", colors.get("selection_foreground", "#fcfcfc"))
        ]
        
        # Добавляем образцы цветов
        for i, (name, color) in enumerate(color_samples):
            # Метка с названием цвета
            name_label = Gtk.Label(label=name)
            name_label.set_xalign(0)
            samples_grid.attach(name_label, 0, i, 1, 1)
            
            # Значение цвета
            value_label = Gtk.Label(label=color)
            value_label.set_xalign(0)
            samples_grid.attach(value_label, 1, i, 1, 1)
            
            # Образец цвета
            color_frame = Gtk.Frame()
            color_frame.set_size_request(50, 20)
            
            # Создаем CSS для образца цвета
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(f"""
            frame {{
                background-color: {color};
                border: 1px solid #000000;
            }}
            """.encode())
            
            # Применяем CSS к образцу
            context = color_frame.get_style_context()
            context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
            samples_grid.attach(color_frame, 2, i, 1, 1)
    
    def on_refresh_clicked(self, button):
        """Обновить цвета и перезагрузить интерфейс"""
        # Пересоздаем окно для обновления цветов
        if self.window:
            self.window.destroy()
            self.window = None
            self.on_activate(self)

def main():
    app = Application()
    return app.run()

if __name__ == "__main__":
    main()