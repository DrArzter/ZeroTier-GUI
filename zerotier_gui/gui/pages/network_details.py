import gi
from zerotier_gui import api
from ...utils import state, format_timestamp

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

class NetworkDetailsPage(Gtk.Box):
    def __init__(self, app, network_id):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.app = app
        self.network_id = network_id
        
        # Основной скролл контейнер
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        self.append(scroll)
        
        # Основной контейнер для контента
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(16)
        self.main_box.set_margin_top(16)
        self.main_box.set_margin_bottom(16)
        scroll.set_child(self.main_box)
        
        # Контейнер для заголовка и кнопки браузера
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(16)
        self.main_box.append(header_box)
        
        # Заголовок сети
        self.network_title = Gtk.Label()
        self.network_title.set_markup("<span size='x-large' weight='bold'>Network Details</span>")
        self.network_title.set_halign(Gtk.Align.START)
        header_box.append(self.network_title)
        
        # Пустой расширяющийся элемент
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header_box.append(spacer)
        
        # Кнопка для открытия в браузере
        browser_btn = Gtk.Button()
        browser_btn.set_icon_name("web-browser-symbolic")
        browser_btn.set_tooltip_text("Open in Browser")
        browser_btn.connect("clicked", self.on_browser_clicked)
        header_box.append(browser_btn)
        
        # Контейнер для информации о сети
        self.info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.info_box.add_css_class("network-info")
        self.main_box.append(self.info_box)
        
        # Заголовок списка участников
        members_title = Gtk.Label()
        members_title.set_markup("<span size='large' weight='bold'>Network Members</span>")
        members_title.set_halign(Gtk.Align.START)
        members_title.set_margin_top(16)
        self.main_box.append(members_title)
        
        # Список участников
        self.members_list = Gtk.ListBox()
        self.members_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.members_list.add_css_class("members-list")
        self.main_box.append(self.members_list)
        
        # Загружаем данные
        GLib.idle_add(self.load_data)
    
    def load_data(self):
        self.app.run_async(self._load_data())
    
    async def _load_data(self):
        # Проверяем кэш для сети
        network = state.get_cached_network(self.network_id)
        if network is None:
            network = await api.get_network_by_id(self.network_id)
            state.update_network_cache(self.network_id, network=network)
        
        def update_network_info():
            # Обновляем заголовок
            name = network.get('config', {}).get('name', '')
            display_name = name if name else f"{network['id']} (unnamed)"
            self.network_title.set_markup(
                f"<span size='x-large' weight='bold'>{display_name}</span>"
            )
            
            # Очищаем текущую информацию
            while self.info_box.get_first_child():
                self.info_box.remove(self.info_box.get_first_child())
            
            # Добавляем основную информацию
            info_items = [
                ("Network ID", network['id']),
                ("Name", name if name else "(unnamed)"),
                ("Description", network.get('description', 'No description')),
                ("Creation Time", format_timestamp(network['config'].get('creationTime', 0))),
                ("Last Online", format_timestamp(network.get('clock', 0))),
                ("Private", "Yes" if network.get('private', False) else "No"),
                ("IPv4 Assignment", "Enabled" if network.get('v4AssignMode', {}).get('zt', False) else "Disabled"),
                ("IPv6 Assignment", "Enabled" if network.get('v6AssignMode', {}).get('zt', False) else "Disabled"),
                ("Route Count", str(len(network.get('routes', [])))),
                ("Rule Count", str(len(network.get('rules', []))))
            ]
            
            for label, value in info_items:
                item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                
                label_widget = Gtk.Label()
                label_widget.set_markup(f"<b>{label}:</b>")
                label_widget.set_halign(Gtk.Align.START)
                item_box.append(label_widget)
                
                value_widget = Gtk.Label(label=str(value))
                value_widget.set_halign(Gtk.Align.START)
                value_widget.set_wrap(True)
                value_widget.set_selectable(True)
                item_box.append(value_widget)
                
                self.info_box.append(item_box)
        
        GLib.idle_add(update_network_info)
        
        # Проверяем кэш для участников
        members = state.get_cached_members(self.network_id)
        if members is None:
            members = await api.get_network_members(self.network_id)
            state.update_network_cache(self.network_id, members=members)
        
        def update_members():
            # Импортируем MemberRow здесь, чтобы избежать циклической зависимости
            from ..components import MemberRow
            
            # Очищаем список
            while self.members_list.get_first_child():
                self.members_list.remove(self.members_list.get_first_child())
            
            # Добавляем участников
            for member in members:
                row = MemberRow(member, self.network_id, self.app)
                self.members_list.append(row)
        
        GLib.idle_add(update_members)
    
    def on_browser_clicked(self, button):
        import subprocess
        import os
        
        url = f"https://my.zerotier.com/network/{self.network_id}"
        
        # Проверяем, запущено ли приложение с правами root
        real_uid = os.environ.get('PKEXEC_UID')
        if real_uid:
            try:
                # Получаем имя пользователя по UID
                import pwd
                user = pwd.getpwuid(int(real_uid)).pw_name
                
                # Сохраняем текущие переменные окружения
                display = os.environ.get('DISPLAY', ':0')
                xdg_runtime = f"/run/user/{real_uid}"
                dbus_session = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
                
                # Формируем команду с сохранением переменных окружения
                cmd = [
                    'su',
                    user,
                    '-c',
                    f'DISPLAY={display} XDG_RUNTIME_DIR={xdg_runtime} DBUS_SESSION_BUS_ADDRESS={dbus_session} xdg-open {url}'
                ]
                
                subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
            except (KeyError, ValueError):
                print(f"Could not find user for UID {real_uid}")
        else:
            # Если приложение запущено без root, просто открываем URL
            subprocess.Popen(['xdg-open', url], stderr=subprocess.DEVNULL) 