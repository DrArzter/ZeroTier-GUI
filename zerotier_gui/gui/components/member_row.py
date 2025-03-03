import gi
from zerotier_gui import api
from ...utils import state

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

class MemberRow(Gtk.ListBoxRow):
    def __init__(self, member, network_id, app):
        super().__init__()
        self.member = member
        self.network_id = network_id
        self.app = app
        
        # Основной контейнер
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("list-row-box")
        self.set_child(box)
        
        # Левая часть с информацией
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.add_css_class("list-row-info")
        box.append(info_box)
        
        # Контейнер для имени и метки "You"
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        info_box.append(name_box)
        
        # Имя участника
        name = member.get('name', 'Unnamed')
        name_label = Gtk.Label(label=f"Name: {name}")
        name_label.set_halign(Gtk.Align.START)
        name_box.append(name_label)

        # Добавляем метку "You" если это текущий пользователь
        if state.is_me(member['config']['address']):
            you_label = Gtk.Label(label="(You)")
            you_label.add_css_class("you-label")
            name_box.append(you_label)
        
        # IP адрес
        ip = 'No IP'
        if 'config' in member and 'ipAssignments' in member['config'] and member['config']['ipAssignments']:
            ip = member['config']['ipAssignments'][0]
        ip_label = Gtk.Label(label=f"IP: {ip}")
        ip_label.set_halign(Gtk.Align.START)
        info_box.append(ip_label)
        
        # Пустой расширяющийся элемент
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        box.append(spacer)
        
        # Правая часть с кнопками
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        buttons_box.add_css_class("list-row-buttons")
        box.append(buttons_box)
        
        ping_btn = Gtk.Button(label="Ping")
        ping_btn.connect("clicked", self.on_ping_clicked)
        buttons_box.append(ping_btn)
    
    def on_ping_clicked(self, button):
        button.set_sensitive(False)  # Отключаем кнопку на время пинга
        button.set_label("Pinging...")
        self.app.run_async(self.ping_member(button))
    
    async def ping_member(self, button):
        try:
            result = await api.ping_member(self.member)
            
            def show_result():
                # Включаем кнопку обратно
                button.set_sensitive(True)
                button.set_label("Ping")
                
                # Создаем диалог с результатом
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_root(),
                    modal=True,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.NONE,  # Убираем стандартные кнопки
                )
                
                # Создаем контейнер для содержимого
                content_area = dialog.get_content_area()
                content_area.set_margin_start(24)
                content_area.set_margin_end(24)
                content_area.set_margin_top(24)
                content_area.set_margin_bottom(24)
                content_area.set_spacing(16)
                
                # Создаем бокс с фоном для контента
                content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                content_box.add_css_class("dialog-content")
                content_box.set_margin_bottom(24)
                content_area.append(content_box)
                
                # Заголовок
                title = Gtk.Label()
                title.set_markup(f"<span size='larger' weight='bold'>Ping Result for {self.member.get('name', 'Unnamed')}</span>")
                title.set_justify(Gtk.Justification.CENTER)
                title.set_halign(Gtk.Align.CENTER)
                content_box.append(title)
                
                # Результат
                result_label = Gtk.Label(label=result)
                result_label.set_justify(Gtk.Justification.CENTER)
                result_label.set_halign(Gtk.Align.CENTER)
                result_label.set_margin_top(8)
                
                # Добавляем контейнер для текста с отдельным фоном
                text_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                text_area.add_css_class("dialog-text-area")
                text_area.append(result_label)
                content_box.append(text_area)
                
                # Добавляем кнопку OK
                button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                button_box.set_halign(Gtk.Align.CENTER)
                
                ok_button = Gtk.Button(label="OK")
                ok_button.add_css_class("suggested-action")
                ok_button.add_css_class("dialog-button")
                ok_button.connect("clicked", lambda b: dialog.destroy())
                button_box.append(ok_button)
                
                content_area.append(button_box)
                
                dialog.present()
            
            GLib.idle_add(show_result)
            
        except Exception as e:
            def show_error():
                # Включаем кнопку обратно
                button.set_sensitive(True)
                button.set_label("Ping")
                
                # Показываем ошибку
                dialog = Gtk.MessageDialog(
                    transient_for=self.get_root(),
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.NONE,  # Убираем стандартные кнопки
                )
                
                # Создаем контейнер для содержимого
                content_area = dialog.get_content_area()
                content_area.set_margin_start(24)
                content_area.set_margin_end(24)
                content_area.set_margin_top(24)
                content_area.set_margin_bottom(24)
                content_area.set_spacing(16)
                
                # Создаем бокс с фоном для контента
                content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                content_box.add_css_class("dialog-content")
                content_box.set_margin_bottom(24)
                content_area.append(content_box)
                
                # Заголовок
                title = Gtk.Label()
                title.set_markup("<span size='larger' weight='bold'>Ping Error</span>")
                title.set_justify(Gtk.Justification.CENTER)
                title.set_halign(Gtk.Align.CENTER)
                content_box.append(title)
                
                # Текст ошибки
                error_label = Gtk.Label(label=str(e))
                error_label.set_justify(Gtk.Justification.CENTER)
                error_label.set_halign(Gtk.Align.CENTER)
                error_label.set_margin_top(8)
                
                # Добавляем контейнер для текста ошибки с отдельным фоном
                text_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                text_area.add_css_class("dialog-text-area")
                text_area.append(error_label)
                content_box.append(text_area)
                
                # Добавляем кнопку OK
                button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                button_box.set_halign(Gtk.Align.CENTER)
                
                ok_button = Gtk.Button(label="OK")
                ok_button.add_css_class("suggested-action")
                ok_button.add_css_class("dialog-button")
                ok_button.connect("clicked", lambda b: dialog.destroy())
                button_box.append(ok_button)
                
                content_area.append(button_box)
                
                dialog.present()
            
            GLib.idle_add(show_error) 