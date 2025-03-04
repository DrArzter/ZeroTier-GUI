import gi
from zerotier_gui import api

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

class JoinNetworkPage(Gtk.Box):
    def __init__(self, app, on_back_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.app = app
        self.on_back_callback = on_back_callback
        
        # Добавляем CSS-классы
        self.add_css_class("join-network-page")
        self.add_css_class("app-page")
        
        # Заголовок
        header = Gtk.Label()
        header.set_markup("<span size='x-large' weight='bold'>Join Network</span>")
        header.set_halign(Gtk.Align.START)
        header.set_margin_bottom(16)
        self.append(header)
        
        # Описание
        description = Gtk.Label(label="Enter the Network ID you want to join:")
        description.set_halign(Gtk.Align.START)
        description.set_margin_bottom(8)
        self.append(description)
        
        # Поле ввода
        self.network_id_entry = Gtk.Entry()
        self.network_id_entry.set_placeholder_text("e.g. 8056c2e21c000001")
        self.network_id_entry.set_margin_bottom(24)
        self.append(self.network_id_entry)
        
        # Контейнер для кнопок
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.START)
        self.append(button_box)
        
        # Кнопка "Назад"
        back_button = Gtk.Button(label="Back")
        back_button.connect("clicked", self.on_back_clicked)
        button_box.append(back_button)
        
        # Кнопка "Присоединиться"
        join_button = Gtk.Button(label="Join Network")
        join_button.connect("clicked", self.on_join_clicked)
        button_box.append(join_button)
        
        # Индикатор статуса
        self.status_label = Gtk.Label()
        self.status_label.set_margin_top(16)
        self.status_label.set_visible(False)
        self.append(self.status_label)
        
        # Спиннер загрузки
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(32, 32)
        self.spinner.set_visible(False)
        self.append(self.spinner)
    
    def on_back_clicked(self, button):
        if self.on_back_callback:
            self.on_back_callback()
    
    def on_join_clicked(self, button):
        network_id = self.network_id_entry.get_text().strip()
        if not network_id:
            self.show_status("Please enter a Network ID", is_error=True)
            return
        
        # Показываем индикатор загрузки
        self.spinner.set_visible(True)
        self.spinner.start()
        self.show_status("Joining network...")
        
        # Присоединяемся к сети
        self.app.run_async(self._join_network(network_id))
    
    async def _join_network(self, network_id):
        try:
            success = await api.join_network(network_id)
            
            def update_ui():
                self.spinner.stop()
                self.spinner.set_visible(False)
                
                if success:
                    self.show_status(f"Successfully joined network {network_id}", is_success=True)
                    # Очищаем поле ввода
                    self.network_id_entry.set_text("")
                else:
                    self.show_status(f"Failed to join network {network_id}", is_error=True)
            
            GLib.idle_add(update_ui)
        except Exception as e:
            def show_error():
                self.spinner.stop()
                self.spinner.set_visible(False)
                self.show_status(f"Error joining network: {str(e)}", is_error=True)
            GLib.idle_add(show_error)
    
    def show_status(self, message, is_error=False, is_success=False):
        self.status_label.set_text(message)
        
        # Удаляем все CSS-классы
        self.status_label.remove_css_class("error-message")
        self.status_label.remove_css_class("success-message")
        
        # Добавляем соответствующий CSS-класс
        if is_error:
            self.status_label.add_css_class("error-message")
        elif is_success:
            self.status_label.add_css_class("success-message")
        
        self.status_label.set_visible(True) 