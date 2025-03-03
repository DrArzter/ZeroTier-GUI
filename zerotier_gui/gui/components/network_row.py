import gi
from zerotier_gui import api
from ...utils import state
from .member_row import MemberRow

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from ..pages.network_details import NetworkDetailsPage

class NetworkRow(Gtk.ListBoxRow):
    def __init__(self, network, app):
        super().__init__()
        self.network = network
        self.app = app
        
        # Основной вертикальный контейнер
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
        
        # Контейнер для информации о сети
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("list-row-box")
        self.main_box.append(box)
        
        # Левая часть с информацией
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.add_css_class("list-row-info")
        box.append(info_box)
        
        # Название сети
        network_name = Gtk.Label()
        name = network.get('config', {}).get('name', '')
        display_name = name if name else f"{network['id']} (unnamed)"
        network_name.set_markup(f"<b>{display_name}</b>")
        network_name.set_halign(Gtk.Align.START)
        network_name.set_selectable(True)
        network_name.set_can_focus(False)
        info_box.append(network_name)
        
        # ID сети
        network_id = Gtk.Label(label=f"ID: {network['id']}")
        network_id.set_halign(Gtk.Align.START)
        network_id.add_css_class("network-id")
        network_id.set_selectable(True)
        network_id.set_can_focus(False)
        info_box.append(network_id)
        
        # Пустой расширяющийся элемент
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        box.append(spacer)
        
        # Правая часть с кнопками
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        buttons_box.add_css_class("list-row-buttons")
        box.append(buttons_box)
        
        members_btn = Gtk.Button(label="Show Members")
        members_btn.connect("clicked", self.on_members_clicked)
        buttons_box.append(members_btn)
        
        details_btn = Gtk.Button(label="Details")
        details_btn.connect("clicked", self.on_details_clicked)
        buttons_box.append(details_btn)
        
        # Контейнер для списка участников (изначально скрыт)
        self.members_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.members_box.set_visible(False)
        self.members_box.add_css_class("members-box")
        self.main_box.append(self.members_box)

        self.members_list = Gtk.ListBox()
        self.members_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.members_list.add_css_class("members-list")
        self.members_box.append(self.members_list)
        
    def on_members_clicked(self, button):
        if self.members_box.get_visible():
            self.members_box.set_visible(False)
            button.set_label("Show Members")
        else:
            self.update_members_list()
            button.set_label("Hide Members")
    
    def update_members_list(self):
        # Получаем кэшированных участников
        members = state.get_cached_members(self.network['id'])
        
        # Показываем спиннер загрузки
        self.show_loading_placeholder()
        
        # Если в кэше нет данных, загружаем их
        if members is None:
            self.app.run_async(self.load_members())
        else:
            self.show_members(members)
    
    def show_members(self, members):
        # Очищаем список
        while self.members_list.get_first_child():
            self.members_list.remove(self.members_list.get_first_child())
        
        # Если список пуст, показываем сообщение с возможностью присоединиться
        if not members:
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            empty_box.set_margin_top(8)
            empty_box.set_margin_bottom(8)
            empty_box.add_css_class("empty-state")
            
            # Добавляем тултип
            empty_box.set_tooltip_text("Click to join this network")
            
            # Делаем box кликабельным
            gesture = Gtk.GestureClick.new()
            gesture.connect("pressed", self.on_empty_state_clicked)
            empty_box.add_controller(gesture)
            
            # Пробуем другую стандартную иконку
            icon = Gtk.Image.new_from_icon_name("network-workgroup-symbolic")
            icon.set_pixel_size(48)
            icon.add_css_class("empty-icon")
            empty_box.append(icon)
            
            label = Gtk.Label(label="No members in this network")
            label.add_css_class("empty-label")
            empty_box.append(label)
            
            self.members_list.append(empty_box)
        else:
            # Добавляем участников
            for member in members:
                row = MemberRow(member, self.network['id'], self.app)
                self.members_list.append(row)
        
        self.members_box.set_visible(True)
    
    def show_loading_placeholder(self):
        # Очищаем список
        while self.members_list.get_first_child():
            self.members_list.remove(self.members_list.get_first_child())
        
        # Создаем контейнер для спиннера
        placeholder_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        placeholder_box.set_margin_top(16)
        placeholder_box.set_margin_bottom(16)
        placeholder_box.set_halign(Gtk.Align.CENTER)
        
        # Добавляем спиннер
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        placeholder_box.append(spinner)
        
        # Добавляем текст
        label = Gtk.Label(label="Loading members...")
        label.add_css_class("dim-label")
        placeholder_box.append(label)
        
        self.members_list.append(placeholder_box)
        self.members_box.set_visible(True)
    
    async def load_members(self):
        members = await api.get_network_members(self.network['id'])
        # Обновляем кэш
        state.update_network_cache(self.network['id'], members=members)
        def update():
            self.show_members(members)
        GLib.idle_add(update)
    
    def on_details_clicked(self, button):
        # Получаем главное окно
        window = self.get_root()
        if window:
            window.show_network_details(self.network['id'])
    
    def on_empty_state_clicked(self, gesture, n_press, x, y):
        self.app.run_async(self.join_network())

    async def join_network(self):
        success = await api.join_network(self.network['id'])
        if success:
            # Перезагружаем список участников
            await self.load_members() 