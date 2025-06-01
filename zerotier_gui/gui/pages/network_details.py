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

        self.add_css_class("app-page")
        self.add_css_class("network-details-page")

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

        # Заголовок сети
        self.network_title = Gtk.Label()
        self.network_title.set_markup(
            "<span size='x-large' weight='bold'>Network Details</span>"
        )
        self.network_title.set_halign(Gtk.Align.START)
        header_box.append(self.network_title)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header_box.append(spacer)

        self.network_action_btn = Gtk.Button()
        self.network_action_btn.set_tooltip_text("Loading...")
        self.network_action_btn.connect("clicked", self.on_network_action_clicked)
        header_box.append(self.network_action_btn)

        self.set_name_btn = Gtk.Button()
        self.set_name_btn.set_icon_name("document-edit-symbolic")
        self.set_name_btn.set_tooltip_text("Set Station Name")
        self.set_name_btn.connect("clicked", self.on_set_name_clicked)
        self.set_name_btn.set_visible(False)
        header_box.append(self.set_name_btn)

        self.manage_network_btn = Gtk.Button()
        self.manage_network_btn.set_icon_name("system-run-symbolic")
        self.manage_network_btn.set_tooltip_text("Manage Network")
        self.manage_network_btn.connect("clicked", self.on_manage_network_clicked)
        self.manage_network_btn.set_visible(False)
        header_box.append(self.manage_network_btn)

        # Кнопка для открытия в браузере
        browser_btn = Gtk.Button()
        browser_btn.set_icon_name("web-browser-symbolic")
        browser_btn.set_tooltip_text("Open in Browser")
        browser_btn.connect("clicked", self.on_browser_clicked)
        header_box.append(browser_btn)

        # Контейнер для информации о сети
        self.info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.info_box.add_css_class("network-info")
        self.info_box.set_halign(Gtk.Align.FILL)
        self.info_box.set_hexpand(True)
        self.main_box.append(self.info_box)

        separator = Gtk.Box()
        separator.set_size_request(-1, 1)
        separator.add_css_class("section-separator")
        separator.set_margin_top(4)
        separator.set_margin_bottom(4)
        self.main_box.append(separator)

        members_title = Gtk.Label()
        members_title.set_markup(
            "<span size='large' weight='bold'>Network Members</span>"
        )
        members_title.set_halign(Gtk.Align.START)
        members_title.set_margin_top(4)
        self.main_box.append(members_title)

        self.members_list = Gtk.ListBox()
        self.members_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.members_list.add_css_class("members-list")
        self.main_box.append(self.members_list)

        GLib.idle_add(self.load_data)

    def load_data(self, force_refresh=False):
        async def _load_with_param():
            await self._load_data(force_refresh)

        self.app.run_async(_load_with_param())

    async def _load_data(self, force_refresh=False):

        if force_refresh:
            state.update_network_cache(self.network_id, network=None, members=None)

        network = state.get_cached_network(self.network_id)
        if network is None:
            network = await api.get_network_by_id(self.network_id)
            state.update_network_cache(self.network_id, network=network)

        is_member = await api.is_member_of_network(self.network_id)

        is_owner = await api.is_network_owner(self.network_id)

        def update_buttons():

            if is_member:
                self.network_action_btn.set_icon_name("network-offline-symbolic")
                self.network_action_btn.set_tooltip_text("Leave Network")
                self.set_name_btn.set_visible(True)
            else:
                self.network_action_btn.set_icon_name(
                    "network-transmit-receive-symbolic"
                )
                self.network_action_btn.set_tooltip_text("Join Network")
                self.set_name_btn.set_visible(False)

            self.manage_network_btn.set_visible(is_owner)

            if is_owner:
                self.network_title.add_css_class("network-owner")
            elif hasattr(self, "owner_icon") and self.owner_icon.get_parent():
                self.owner_icon.get_parent().remove(self.owner_icon)
                self.network_title.remove_css_class("network-owner")

        GLib.idle_add(update_buttons)

        def update_network_info():
            name = network.get("config", {}).get("name", "")
            display_name = name if name else f"{network['id']} (unnamed)"

            self.network_title.set_markup(
                f"<span size='x-large' weight='bold'>{display_name}</span>"
            )

            if is_owner:
                self.network_title.set_tooltip_text("You are the owner of this network")
            else:
                self.network_title.set_tooltip_text(None)

            while self.info_box.get_first_child():
                self.info_box.remove(self.info_box.get_first_child())

            info_items = [
                ("Network ID", network["id"]),
                ("Name", name if name else "(unnamed)"),
                ("Description", network.get("description", "No description")),
                (
                    "Owner ID",
                    network.get("ownerId", "Unknown") + (" (You)" if is_owner else ""),
                ),
                (
                    "Creation Time",
                    format_timestamp(network["config"].get("creationTime", 0)),
                ),
                ("Last Online", format_timestamp(network.get("clock", 0))),
                (
                    "Private",
                    "Yes" if network.get("config", {}).get("private", False) else "No",
                ),
                ("MTU", str(network.get("config", {}).get("mtu", "Default"))),
                (
                    "Multicast Limit",
                    str(network.get("config", {}).get("multicastLimit", "Default")),
                ),
                (
                    "Broadcast",
                    (
                        "Enabled"
                        if network.get("config", {}).get("enableBroadcast", False)
                        else "Disabled"
                    ),
                ),
            ]

            v4_assign = network.get("config", {}).get("v4AssignMode", {})
            v6_assign = network.get("config", {}).get("v6AssignMode", {})

            ip_assignment_items = [
                (
                    "IPv4 Assignment (ZT)",
                    "Enabled" if v4_assign.get("zt", False) else "Disabled",
                ),
                (
                    "IPv6 Assignment (ZT)",
                    "Enabled" if v6_assign.get("zt", False) else "Disabled",
                ),
                (
                    "IPv6 6PLANE",
                    "Enabled" if v6_assign.get("6plane", False) else "Disabled",
                ),
                (
                    "IPv6 RFC4193",
                    "Enabled" if v6_assign.get("rfc4193", False) else "Disabled",
                ),
            ]

            ip_pools = network.get("config", {}).get("ipAssignmentPools", [])
            if ip_pools:
                pool_strings = []
                for pool in ip_pools:
                    start = pool.get("ipRangeStart", "")
                    end = pool.get("ipRangeEnd", "")
                    if start and end:
                        pool_strings.append(f"{start} - {end}")

                if pool_strings:
                    ip_assignment_items.append(
                        ("IP Assignment Pools", "\n".join(pool_strings))
                    )
                else:
                    ip_assignment_items.append(("IP Assignment Pools", "None"))
            else:
                ip_assignment_items.append(("IP Assignment Pools", "None"))

            dns = network.get("config", {}).get("dns", {})
            dns_domain = dns.get("domain", "")
            dns_servers = dns.get("servers", [])

            dns_items = [
                ("DNS Domain", dns_domain if dns_domain else "Not set"),
                ("DNS Servers", ", ".join(dns_servers) if dns_servers else "Not set"),
            ]

            stats_items = [
                ("Online Members", str(network.get("onlineMemberCount", 0))),
                ("Authorized Members", str(network.get("authorizedMemberCount", 0))),
                ("Total Members", str(network.get("totalMemberCount", 0))),
                ("Route Count", str(len(network.get("config", {}).get("routes", [])))),
                ("Rule Count", str(len(network.get("config", {}).get("rules", [])))),
            ]

            sso_items = []
            sso_config = network.get("config", {}).get("ssoConfig", {})
            if sso_config:
                sso_items.extend(
                    [
                        (
                            "SSO Enabled",
                            "Yes" if sso_config.get("enabled", False) else "No",
                        ),
                        ("SSO Mode", sso_config.get("mode", "Not set")),
                    ]
                )

            rules_source = network.get("rulesSource", "")

            sections = [
                ("Basic Information", info_items[:6]),
                ("Network Configuration", info_items[6:10]),
                ("IP Assignment", ip_assignment_items),
                ("DNS Configuration", dns_items),
                ("Statistics", stats_items),
            ]

            if sso_items:
                sections.append(("SSO Configuration", sso_items))

            first_section = True
            for section_title, section_items in sections:

                section_label = Gtk.Label()
                section_label.set_markup(
                    f"<span size='large' weight='bold'>{section_title}</span>"
                )
                section_label.set_halign(Gtk.Align.START)
                section_label.set_xalign(0.0)

                if first_section:
                    section_label.set_margin_top(0)
                    first_section = False
                else:
                    section_label.set_margin_top(8)

                section_label.set_margin_bottom(4)
                section_label.add_css_class("network-info-section-title")
                self.info_box.append(section_label)

                section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                section_box.add_css_class("network-info-section")
                section_box.set_hexpand(True)
                section_box.set_halign(Gtk.Align.FILL)
                self.info_box.append(section_box)

                for label, value in section_items:
                    item_box = Gtk.Box(
                        orientation=Gtk.Orientation.HORIZONTAL, spacing=8
                    )
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

            if rules_source:

                rules_label = Gtk.Label()
                rules_label.set_markup(
                    "<span size='large' weight='bold'>Rules Source</span>"
                )
                rules_label.set_halign(Gtk.Align.START)
                rules_label.set_xalign(0.0)
                rules_label.set_margin_top(8)
                rules_label.set_margin_bottom(4)
                rules_label.add_css_class("network-info-section-title")
                self.info_box.append(rules_label)

                rules_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                rules_section.add_css_class("network-info-section")
                rules_section.set_hexpand(True)
                rules_section.set_halign(Gtk.Align.FILL)
                self.info_box.append(rules_section)

                rules_view = Gtk.TextView()
                rules_view.set_editable(False)
                rules_view.set_cursor_visible(False)
                rules_view.set_wrap_mode(Gtk.WrapMode.WORD)
                rules_view.get_buffer().set_text(rules_source)
                rules_view.add_css_class("rules-source")

                rules_scroll = Gtk.ScrolledWindow()
                rules_scroll.set_min_content_height(200)
                rules_scroll.set_vexpand(True)
                rules_scroll.set_child(rules_view)
                rules_scroll.add_css_class("rules-scroll")

                rules_section.append(rules_scroll)

                rules_section.add_css_class("no-bottom-border")

        GLib.idle_add(update_network_info)

        members = state.get_cached_members(self.network_id)
        if members is None:
            members = await api.get_network_members(self.network_id)
            state.update_network_cache(self.network_id, members=members)

        def update_members():
            #
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

        real_uid = os.environ.get("PKEXEC_UID")
        if real_uid:
            try:
                import pwd

                user = pwd.getpwuid(int(real_uid)).pw_name

                display = os.environ.get("DISPLAY", ":0")
                xdg_runtime = f"/run/user/{real_uid}"
                dbus_session = os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")

                cmd = [
                    "su",
                    user,
                    "-c",
                    f"DISPLAY={display} XDG_RUNTIME_DIR={xdg_runtime} DBUS_SESSION_BUS_ADDRESS={dbus_session} xdg-open {url}",
                ]

                subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
            except (KeyError, ValueError):
                pass
        else:

            subprocess.Popen(["xdg-open", url], stderr=subprocess.DEVNULL)

    def on_network_action_clicked(self, button):
        """Обрабатывает нажатие на кнопку подключения/отключения от сети."""
        self.app.run_async(self._handle_network_action())

    async def _handle_network_action(self):

        is_member = await api.is_member_of_network(self.network_id)

        if is_member:

            success = await api.leave_network(self.network_id)
            if success:

                def update_ui():
                    self.network_action_btn.set_icon_name(
                        "network-transmit-receive-symbolic"
                    )
                    self.network_action_btn.set_tooltip_text("Join Network")
                    self.set_name_btn.set_visible(False)
                    window = self.app.window
                    if window:
                        window.show_message_dialog(
                            "Network Action",
                            "Successfully left the network",
                            Gtk.MessageType.INFO,
                        )

                GLib.idle_add(update_ui)
            else:
                window = self.app.window
                if window:
                    window.show_message_dialog(
                        "Network Action",
                        "Failed to leave the network",
                        Gtk.MessageType.ERROR,
                    )
        else:

            is_member_double_check = await api.is_member_of_network(self.network_id)
            if is_member_double_check:

                def update_ui():
                    self.network_action_btn.set_icon_name("network-offline-symbolic")
                    self.network_action_btn.set_tooltip_text("Leave Network")
                    self.set_name_btn.set_visible(True)
                    window = self.app.window
                    if window:
                        window.show_message_dialog(
                            "Network Action",
                            "You are already a member of this network",
                            Gtk.MessageType.INFO,
                        )

                GLib.idle_add(update_ui)

                self.app.run_async(self._load_data(force_refresh=True))
                return

            success = await api.join_network(self.network_id)
            if success:

                await self._set_default_station_name()

                def update_ui():
                    self.network_action_btn.set_icon_name("network-offline-symbolic")
                    self.network_action_btn.set_tooltip_text("Leave Network")
                    self.set_name_btn.set_visible(True)

                    if window:
                        window.show_message_dialog(
                            "Network Action",
                            "Successfully joined the network",
                            Gtk.MessageType.INFO,
                        )

                GLib.idle_add(update_ui)
            else:
                window = self.app.window
                if window:
                    window.show_message_dialog(
                        "Network Action",
                        "Failed to join the network",
                        Gtk.MessageType.ERROR,
                    )

    def on_set_name_clicked(self, button):
        """Обрабатывает нажатие на кнопку установки имени станции."""

        dialog = Gtk.Dialog(
            title="Set Station Name", transient_for=self.app.get_active_window()
        )
        dialog.add_css_class("message-dialog")

        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Set", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        content_area = dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)

        label = Gtk.Label(label="Enter station name:")
        label.set_halign(Gtk.Align.START)
        content_area.append(label)

        entry = Gtk.Entry()
        entry.set_activates_default(True)

        import os
        import socket

        default_name = f"{os.getlogin()}@{socket.gethostname()}"
        entry.set_text(default_name)

        content_area.append(entry)

        dialog.connect("response", self._on_name_dialog_response, entry)
        dialog.show()

    def _on_name_dialog_response(self, dialog, response_id, entry):
        """Обрабатывает ответ диалога установки имени."""
        if response_id == Gtk.ResponseType.OK:
            name = entry.get_text()
            if name:
                self.app.run_async(self._set_station_name(name))

        dialog.destroy()

    async def _set_station_name(self, name):
        """Устанавливает имя станции в сети."""
        success = await api.set_station_name(name, self.network_id)
        if success:
            window = self.app.window
            if window:
                window.show_message_dialog(
                    "Station Name", f"Station name set to: {name}", Gtk.MessageType.INFO
                )

                self.app.run_async(self._load_data(force_refresh=True))
        else:
            window = self.app.window
            if window:
                window.show_message_dialog(
                    "Station Name",
                    "Failed to set station name. Make sure the application has sudo privileges.",
                    Gtk.MessageType.ERROR,
                )

    async def _set_default_station_name(self):
        """Устанавливает имя станции по умолчанию при подключении к сети."""
        import os
        import socket

        default_name = f"{os.getlogin()}@{socket.gethostname()}"
        await api.set_station_name(default_name, self.network_id)

    def on_manage_network_clicked(self, button):
        """Обрабатывает нажатие на кнопку управления сетью."""

        popover = Gtk.Popover()
        popover.set_parent(button)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_margin_start(6)
        box.set_margin_end(6)

        edit_btn = Gtk.Button(label="Edit Network Settings")
        edit_btn.connect("clicked", self.on_edit_network_clicked)
        edit_btn.add_css_class("flat")
        box.append(edit_btn)

        delete_btn = Gtk.Button(label="Delete Network")
        delete_btn.connect("clicked", self.on_delete_network_clicked)
        delete_btn.add_css_class("flat")
        delete_btn.add_css_class("destructive-action")
        box.append(delete_btn)

        popover.set_child(box)

        popover.popup()

    def on_edit_network_clicked(self, button):
        """Обрабатывает нажатие на кнопку редактирования настроек сети."""

        popover = button.get_parent().get_parent()
        popover.popdown()

        import subprocess

        url = f"https://my.zerotier.com/network/{self.network_id}"
        subprocess.Popen(["xdg-open", url], stderr=subprocess.DEVNULL)

    def on_delete_network_clicked(self, button):
        """Обрабатывает нажатие на кнопку удаления сети."""

        popover = button.get_parent().get_parent()
        popover.popdown()

        dialog = Gtk.Dialog(
            title="Delete Network",
            transient_for=self.app.window,
            modal=True,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Delete", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)

        delete_btn = dialog.get_widget_for_response(Gtk.ResponseType.OK)
        if delete_btn:
            delete_btn.add_css_class("destructive-action")

        content_area = dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)

        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        warning_box.append(warning_icon)

        warning_label = Gtk.Label()
        warning_label.set_markup("<b>Warning:</b> This action cannot be undone!")
        warning_label.set_halign(Gtk.Align.START)
        warning_box.append(warning_label)

        content_area.append(warning_box)

        confirm_label = Gtk.Label()
        confirm_label.set_markup(
            f"Are you sure you want to delete the network <b>{self.network_id}</b>?\n"
            "All members will be disconnected and all network settings will be lost."
        )
        confirm_label.set_wrap(True)
        confirm_label.set_halign(Gtk.Align.START)
        content_area.append(confirm_label)

        dialog.connect("response", self._on_delete_dialog_response)
        dialog.show()

    def _on_delete_dialog_response(self, dialog, response_id):
        """Обрабатывает ответ диалога удаления сети."""
        if response_id == Gtk.ResponseType.OK:
            self.app.run_async(self._delete_network())

        dialog.destroy()

    async def _delete_network(self):
        """Удаляет сеть."""
        try:
            await api.delete_network(self.network_id)

            window = self.app.window
            if window:
                window.show_message_dialog(
                    "Network Deleted",
                    "The network has been successfully deleted.",
                    Gtk.MessageType.INFO,
                )

            window.show_networks_page()
        except Exception as e:
            window = self.app.window
            if window:
                window.show_message_dialog(
                    "Error", f"Failed to delete the network: {e}", Gtk.MessageType.ERROR
                )
