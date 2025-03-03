import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .pages import NetworksPage, SettingsPage, AboutPage
from .styles import load_css

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.set_default_size(800, 600)
        self.set_title("ZeroTier Network Manager")
        self.current_page = None

        # Загружаем стили
        load_css(self)

        # Создаем UI
        self.setup_ui()
        
        # Создаем страницу сетей один раз
        self.networks_page = NetworksPage(self.app)
        
        # Изначально показываем страницу сетей
        self.show_networks_page()

    def setup_ui(self):
        # Создаем overlay для бокового меню
        self.overlay = Gtk.Overlay()
        self.set_child(self.overlay)

        # Основной контейнер
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.overlay.set_child(self.main_box)

        self.setup_header()
        self.setup_sidebar()
        self.setup_content()

    def setup_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.add_css_class("header")
        self.main_box.append(header)

        # Левая часть header
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.append(left_box)

        menu_button = Gtk.Button()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.connect("clicked", self.on_menu_clicked)
        left_box.append(menu_button)

        # ID пользователя
        self.id_label = Gtk.Label()
        self.id_label.add_css_class("user-id-label")
        left_box.append(self.id_label)
        
        # Загружаем ID асинхронно
        self.app.run_async(self.load_user_id())

        # Расширяющийся элемент
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        # Правая часть header
        self.header_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.header_actions.add_css_class("header-actions")
        
        # Название текущей страницы/сети (в начале правой части)
        self.title_label = Gtk.Label(label="Networks")
        self.title_label.add_css_class("page-title")
        self.header_actions.append(self.title_label)
        
        header.append(self.header_actions)

        # Инициализируем кнопку назад
        self.back_button = Gtk.Button()
        self.back_button.set_icon_name("go-previous-symbolic")
        self.back_button.connect("clicked", self.on_back_clicked)
        self.back_button.set_visible(False)

    def setup_sidebar(self):
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.sidebar.set_size_request(200, -1)
        self.sidebar.add_css_class("sidebar")
        self.sidebar.set_visible(False)

        nav_items = [
            ("Networks", self.show_networks_page),
            ("Settings", self.show_settings_page),
            ("About", self.show_about_page),
        ]
        
        for label, callback in nav_items:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            self.sidebar.append(button)

        self.overlay.add_overlay(self.sidebar)

    def setup_content(self):
        content_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_wrapper.set_margin_start(16)
        content_wrapper.set_margin_end(16)
        content_wrapper.set_margin_top(16)
        content_wrapper.set_margin_bottom(16)
        self.main_box.append(content_wrapper)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content_wrapper.append(self.content_box)

    def on_menu_clicked(self, button):
        self.sidebar.set_visible(not self.sidebar.get_visible())

    def on_back_clicked(self, button):
        self.show_networks_page()

    def clear_content(self):
        while self.content_box.get_first_child():
            self.content_box.remove(self.content_box.get_first_child())

    def clear_header_actions(self):
        while self.header_actions.get_first_child():
            self.header_actions.remove(self.header_actions.get_first_child())

    def show_networks_page(self, button=None):
        self.clear_content()
        self.current_page = "networks"
        
        # Очищаем и добавляем кнопки действий для страницы Networks
        self.clear_header_actions()
        
        # Обновляем заголовок
        self.title_label.set_text("Networks")
        
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Networks")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header_actions.append(refresh_btn)
        
        create_btn = Gtk.Button()
        create_btn.set_icon_name("list-add-symbolic")
        create_btn.set_tooltip_text("Create New Network")
        create_btn.connect("clicked", lambda btn: self.networks_page.create_network())
        self.header_actions.append(create_btn)

        # Скрываем кнопку назад
        self.back_button.set_visible(False)

        # Показываем существующую страницу без перезагрузки
        self.content_box.append(self.networks_page)
        self.sidebar.set_visible(False)

    def show_network_details(self, network_id):
        from .pages.network_details import NetworkDetailsPage
        from zerotier_gui import api
        
        self.clear_content()
        self.current_page = ("network_details", network_id)
        
        # Очищаем и добавляем кнопки действий
        self.clear_header_actions()
        
        # Добавляем кнопки в правильном порядке
        self.back_button.set_visible(True)
        self.header_actions.append(self.back_button)
        
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Network Details")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header_actions.append(refresh_btn)
        
        # Создаем и показываем страницу деталей
        details_page = NetworkDetailsPage(self.app, network_id)
        self.content_box.append(details_page)
        self.sidebar.set_visible(False)
        
        # Загружаем и обновляем название сети
        self.app.run_async(self._update_network_title(network_id))
    
    async def _update_network_title(self, network_id):
        from zerotier_gui import api
        try:
            network = await api.get_network_by_id(network_id)
            def update_title():
                name = network.get('config', {}).get('name', '')
                print(f"Network data: {network}")
                print(f"Raw name value: {name!r}")
                print(f"Raw name length: {len(name)}")
                
                display_name = name if name else f"{network_id} (unnamed)"
                print(f"Final name: {display_name!r}")
                
                self.title_label.set_text(display_name)
            from gi.repository import GLib
            GLib.idle_add(update_title)
        except Exception as e:
            print(f"Failed to load network name: {e}")
            self.title_label.set_text(f"Network {network_id}")

    def on_refresh_clicked(self, button):
        if self.current_page == "networks":
            self.networks_page.load_networks()
        elif isinstance(self.current_page, tuple) and self.current_page[0] == "network_details":
            # Получаем текущую страницу деталей сети
            details_page = self.content_box.get_first_child()
            if details_page:
                self.app.run_async(details_page._load_data())

    def show_settings_page(self, button=None):
        self.clear_content()
        self.clear_header_actions()
        self.current_page = "settings"
        page = SettingsPage()
        self.content_box.append(page)
        self.sidebar.set_visible(False)
        self.back_button.set_visible(False)

    def show_about_page(self, button=None):
        self.clear_content()
        self.clear_header_actions()
        self.current_page = "about"
        page = AboutPage()
        self.content_box.append(page)
        self.sidebar.set_visible(False)
        self.back_button.set_visible(False)

    async def load_user_id(self):
        from zerotier_gui import api
        my_id = await api.get_my_id()
        def update_label():
            self.id_label.set_text(f"ID: {my_id}")
        GLib.idle_add(update_label) 