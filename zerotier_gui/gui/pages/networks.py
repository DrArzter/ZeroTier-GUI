from gi.repository import Gtk, GLib
from ..components import NetworkRow, MemberRow
from zerotier_gui import api
from ...utils import state

class NetworksPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.app = app
        self._is_loading = False
        
        # Добавляем общий CSS-класс
        self.add_css_class("app-page")
        
        # Контейнер для списка с отступами
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        self.append(scroll)
        
        # Список сетей
        self.network_list = Gtk.ListBox()
        self.network_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.network_list.add_css_class("network-list")
        scroll.set_child(self.network_list)

        # Загружаем сети
        GLib.idle_add(self.load_networks)

    def load_networks(self):
        if self._is_loading:
            return
        self._is_loading = True
        self.app.run_async(self._load_networks())

    async def _load_networks(self):
        try:
            def clear_list():
                while self.network_list.get_first_child():
                    self.network_list.remove(self.network_list.get_first_child())
            GLib.idle_add(clear_list)
                
            networks = await api.get_networks()
            state.update_networks_cache(networks)
            
            # Загружаем участников для каждой сети
            for network in networks:
                members = await api.get_network_members(network['id'])
                state.update_network_cache(network['id'], members=members)
            
            def add_networks():
                # Если сетей нет, показываем сообщение
                if not networks:
                    empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                    empty_box.set_margin_top(32)
                    empty_box.set_margin_bottom(32)
                    empty_box.set_halign(Gtk.Align.CENTER)
                    empty_box.set_valign(Gtk.Align.CENTER)
                    empty_box.set_vexpand(True)
                    
                    icon = Gtk.Image.new_from_icon_name("network-offline-symbolic")
                    icon.set_pixel_size(48)
                    empty_box.append(icon)
                    
                    label = Gtk.Label(label="No networks found")
                    label.add_css_class("dim-label")
                    empty_box.append(label)
                    
                    self.network_list.append(empty_box)
                else:
                    for network in networks:
                        row = NetworkRow(network, self.app)
                        self.network_list.append(row)
            GLib.idle_add(add_networks)
        finally:
            self._is_loading = False

    def create_network(self):
        self.app.run_async(self._create_network())

    async def _create_network(self):
        network = await api.create_network()
        # Добавляем новую сеть в кэш
        state.update_network_cache(network['id'], network=network)
        def add_network():
            row = NetworkRow(network, self.app)
            self.network_list.append(row)
        GLib.idle_add(add_network)

    def show_members(self, members, network_id):
        while self.members_list.get_first_child():
            self.members_list.remove(self.members_list.get_first_child())
            
        for member in members:
            row = MemberRow(member, network_id, self.app)
            self.members_list.append(row) 