import gi
import json
from datetime import datetime
from loguru import logger

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ... import api
from ...utils import state

class UserInfoPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.app = app
        
        # Добавляем общие CSS-классы
        self.add_css_class("app-page")
        self.add_css_class("user-info-page")
        
        # Основной скролл контейнер (с невидимым скроллбаром)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add_css_class("hidden-scrollbar")
        self.append(scroll)
        
        # Основной контейнер для контента
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        scroll.set_child(self.main_box)
        
        # Контейнер для заголовка и кнопок
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(16)
        self.main_box.append(header_box)
        
        # Заголовок страницы
        self.page_title = Gtk.Label()
        self.page_title.set_markup(
            "<span size='x-large' weight='bold'>User Information</span>"
        )
        self.page_title.set_halign(Gtk.Align.START)
        header_box.append(self.page_title)
        
        # Пустой расширяющийся элемент
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header_box.append(spacer)
        
        # Кнопка обновления
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh User Info")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        header_box.append(refresh_btn)
        
        # Контейнер для информации о пользователе
        self.info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.info_box.add_css_class("network-info")
        self.main_box.append(self.info_box)
        
        # Загружаем данные пользователя
        self.load_data()
    
    def load_data(self):
        async def _load_data():
            await self._load_user_data()
        
        self.app.run_async(_load_data())
    
    async def _load_user_data(self):
        # Получаем данные пользователя
        if not state.user_data:
            await api.initialize_user()
        
        user_data = state.user_data
        
        # Обновляем UI в основном потоке
        GLib.idle_add(self._update_ui, user_data)
    
    def _update_ui(self, user_data):
        # Очищаем контейнер
        while self.info_box.get_first_child():
            self.info_box.remove(self.info_box.get_first_child())
        
        if not user_data:
            label = Gtk.Label(label="Failed to load user data")
            self.info_box.append(label)
            return False
        
        # Подготавливаем данные для отображения в секциях
        sections = []
        
        # Основная информация о пользователе
        basic_info = []
        if 'user' in user_data:
            user = user_data['user']
            basic_info.extend([
                ("Display Name", user.get('displayName', 'N/A')),
                ("Email", user.get('email', 'N/A')),
                ("User ID", user.get('id', 'N/A')),
                ("Organization ID", user.get('orgId', 'N/A')),
                ("Node ID", state.my_id or "N/A")
            ])
            
            # Creation Time
            creation_time = user.get('creationTime', 0)
            if creation_time:
                date_str = datetime.fromtimestamp(creation_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                basic_info.append(("Account Created", date_str))
            
            # Токены
            tokens = user.get('tokens', [])
            if tokens:
                basic_info.append(("API Tokens", ", ".join(tokens)))
        
        sections.append(("Basic Information", basic_info))
        
        # Лимиты аккаунта
        if 'user' in user_data and 'accountLimits' in user_data['user']:
            limits = user_data['user']['accountLimits']
            account_limits = [
                ("Status", "Enabled" if limits.get('enabled', False) else "Disabled"),
                ("Max Networks", str(limits.get('maxNetworks', 0))),
                ("Current Networks", str(limits.get('currentNetworks', 0))),
                ("Max Members", str(limits.get('maxMembers', 0))),
                ("Current Members", str(limits.get('currentMembers', 0))),
                ("Max Admins", str(limits.get('maxAdmins', 0))),
                ("Current Admins", str(limits.get('currentAdmins', 0))),
                ("Max Routes", str(limits.get('maxRoutes', 0))),
                ("Current Routes", str(limits.get('currentRoutes', 0)))
            ]
            sections.append(("Account Limits", account_limits))
        
        # Информация о системе ZeroTier
        system_info = [
            ("API Version", user_data.get('apiVersion', 'N/A')),
            ("Online Status", "Online" if user_data.get('online', False) else "Offline")
        ]
        
        # Время работы
        uptime = user_data.get('uptime', 0)
        if uptime:
            days = uptime // (24 * 60 * 60 * 1000)
            hours = (uptime % (24 * 60 * 60 * 1000)) // (60 * 60 * 1000)
            system_info.append(("Uptime", f"{days} days, {hours} hours"))
        
        system_info.extend([
            ("Cluster Node", user_data.get('clusterNode', 'N/A')),
            ("Read-Only Mode", "Yes" if user_data.get('readOnlyMode', False) else "No")
        ])
        
        sections.append(("ZeroTier System Information", system_info))
        
        # Доступные функции
        if 'features' in user_data:
            features = user_data['features']
            features_info = []
            for key, value in features.items():
                features_info.append((key, "Enabled" if value else "Disabled"))
            
            sections.append(("Available Features", features_info))
        
        # Отображаем все секции
        first_section = True
        for section_title, section_items in sections:
            # Добавляем заголовок секции
            section_label = Gtk.Label()
            section_label.set_markup(f"<span size='large' weight='bold'>{section_title}</span>")
            section_label.set_halign(Gtk.Align.START)
            section_label.set_xalign(0.0)
            
            # Для первой секции меньший отступ сверху
            if first_section:
                section_label.set_margin_top(0)
                first_section = False
            else:
                section_label.set_margin_top(8)
            
            section_label.set_margin_bottom(4)
            section_label.add_css_class("network-info-section-title")
            self.info_box.append(section_label)
            
            # Создаем контейнер для секции
            section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            section_box.add_css_class("network-info-section")
            section_box.set_hexpand(True)
            section_box.set_halign(Gtk.Align.FILL)
            self.info_box.append(section_box)
            
            # Добавляем элементы секции
            for label, value in section_items:
                item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                item_box.add_css_class("network-info-row")
                item_box.set_hexpand(True)
                item_box.set_halign(Gtk.Align.FILL)
                
                label_widget = Gtk.Label()
                label_widget.set_markup(f"<b>{label}:</b>")
                label_widget.set_halign(Gtk.Align.START)
                label_widget.set_xalign(0.0)
                label_widget.set_size_request(150, -1)
                label_widget.add_css_class("network-info-label")
                item_box.append(label_widget)
                
                value_widget = Gtk.Label(label=str(value))
                value_widget.set_halign(Gtk.Align.END)
                value_widget.set_hexpand(True)
                value_widget.set_wrap(True)
                value_widget.set_selectable(True)
                value_widget.set_xalign(1.0)
                value_widget.set_yalign(0.0)
                value_widget.add_css_class("network-info-value")
                item_box.append(value_widget)
                
                section_box.append(item_box)
        
        return False
    
    def on_refresh_clicked(self, button):
        # Очищаем кэш пользователя
        state.user_data = None
        
        # Перезагружаем данные
        self.load_data() 