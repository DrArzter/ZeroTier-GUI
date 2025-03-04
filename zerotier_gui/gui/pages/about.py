import gi
import os
import subprocess

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Gio

class AboutPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        # Добавляем общий CSS-класс
        self.add_css_class("app-page")
        
        # Title
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>ZeroTier GUI</span>")
        self.append(title)
        
        # Description
        description = Gtk.Label(
            label=(
                "A simple and modern GTK4 application for managing ZeroTier networks. "
                "Created as an alternative to the existing solutions, with focus on "
                "native look and feel on KDE Plasma desktop environment."
            )
        )
        description.set_wrap(True)
        description.set_justify(Gtk.Justification.CENTER)
        self.append(description)
        
        # Features
        features_label = Gtk.Label()
        features_label.set_markup("<span weight='bold'>Features:</span>")
        features_label.set_margin_top(16)
        self.append(features_label)
        
        features = Gtk.Label(
            label=(
                "• Native GTK4 interface\n"
                "• KDE Plasma theme integration\n"
                "• Network management\n"
                "• Member management\n"
                "• Easy network joining\n"
                "• Member status monitoring"
            )
        )
        features.set_justify(Gtk.Justification.LEFT)
        features.set_margin_start(20)
        self.append(features)
        
        # License
        license_label = Gtk.Label()
        license_label.set_markup("<span weight='bold'>License:</span>")
        license_label.set_margin_top(16)
        self.append(license_label)
        
        license_text = Gtk.Label(
            label=(
                "This software is released under the MIT License.\n\n"
                "Copyright (c) 2024\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy "
                "of this software and associated documentation files (the \"Software\"), to deal "
                "in the Software without restriction, including without limitation the rights "
                "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
                "copies of the Software, and to permit persons to whom the Software is "
                "furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all "
                "copies or substantial portions of the Software."
            )
        )
        license_text.set_wrap(True)
        license_text.set_justify(Gtk.Justification.CENTER)
        license_text.set_margin_start(20)
        license_text.set_margin_end(20)
        self.append(license_text)
        
        # Links
        links_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        links_box.set_halign(Gtk.Align.CENTER)
        links_box.set_margin_top(16)
        
        github_button = Gtk.Button(label="GitHub")
        github_button.connect("clicked", self.on_link_clicked, "https://github.com/DrArzter/zerotier-gui")
        links_box.append(github_button)
        
        zerotier_button = Gtk.Button(label="ZeroTier")
        zerotier_button.connect("clicked", self.on_link_clicked, "https://www.zerotier.com")
        links_box.append(zerotier_button)
        
        self.append(links_box)

    def on_link_clicked(self, button, url):
        real_uid = os.environ.get('PKEXEC_UID')
        if real_uid:
            # Получаем имя пользователя по UID
            try:
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
                pass
