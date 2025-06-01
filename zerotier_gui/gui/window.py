import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio
from .pages import NetworksPage, SettingsPage, AboutPage, UserInfoPage
from .styles import load_css


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.set_default_size(800, 600)
        self.set_title("ZeroTier Network Manager")
        self.current_page = None

        load_css(self)

        self.setup_ui()

        self.networks_page = NetworksPage(self.app)

        self.show_networks_page()

    def setup_ui(self):

        self.overlay = Gtk.Overlay()
        self.set_child(self.overlay)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.overlay.set_child(self.main_box)

        self.setup_header()
        self.setup_sidebar()
        self.setup_content()

    def setup_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.add_css_class("header")
        self.main_box.append(header)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        left_box.set_margin_start(4)
        header.append(left_box)

        menu_button = Gtk.Button()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.connect("clicked", self.on_menu_clicked)
        left_box.append(menu_button)

        self.id_label = Gtk.Label()
        self.id_label.add_css_class("user-id-label")
        left_box.append(self.id_label)

        self.app.run_async(self.load_user_id())

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        self.header_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.header_actions.add_css_class("header-actions")
        self.header_actions.set_margin_end(4)

        self.title_label = Gtk.Label(label="Networks")
        self.title_label.add_css_class("page-title")
        self.header_actions.append(self.title_label)

        header.append(self.header_actions)

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
            ("User Info", self.show_user_info_page),
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

        self.clear_header_actions()

        self.title_label.set_text("Networks")

        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Networks")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header_actions.append(refresh_btn)
        create_btn = Gtk.MenuButton()
        create_btn.set_icon_name("list-add-symbolic")
        create_btn.set_tooltip_text("Network Actions")

        menu = Gtk.PopoverMenu()
        menu.set_has_arrow(True)
        menu.set_position(Gtk.PositionType.BOTTOM)
        create_btn.set_popover(menu)

        menu_model = Gio.Menu()

        create_action = Gio.SimpleAction.new("create-network", None)
        create_action.connect(
            "activate", lambda a, p: self.networks_page.create_network()
        )
        self.app.add_action(create_action)
        menu_model.append("Create Network", "app.create-network")

        join_action = Gio.SimpleAction.new("join-network", None)
        join_action.connect("activate", lambda a, p: self.show_join_network_page())
        self.app.add_action(join_action)
        menu_model.append("Join Network", "app.join-network")

        menu.set_menu_model(menu_model)

        self.header_actions.append(create_btn)

        self.back_button.set_visible(False)

        self.content_box.append(self.networks_page)
        self.sidebar.set_visible(False)

    def show_network_details(self, network_id):
        from .pages.network_details import NetworkDetailsPage
        from zerotier_gui import api

        self.clear_content()
        self.current_page = ("network_details", network_id)

        self.clear_header_actions()

        self.back_button.set_visible(True)
        self.header_actions.append(self.back_button)

        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Network Details")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header_actions.append(refresh_btn)

        details_page = NetworkDetailsPage(self.app, network_id)
        self.content_box.append(details_page)
        self.sidebar.set_visible(False)

        self.app.run_async(self._update_network_title(network_id))

    async def _update_network_title(self, network_id):
        from zerotier_gui import api

        try:
            network = await api.get_network_by_id(network_id)

            def update_title():
                name = network.get("config", {}).get("name", "")

                display_name = name if name else f"{network_id} (unnamed)"

                self.title_label.set_text(display_name)

            from gi.repository import GLib

            GLib.idle_add(update_title)
        except Exception as e:
            self.title_label.set_text(f"Network {network_id}")

    def on_refresh_clicked(self, button):
        if self.current_page == "networks":
            self.networks_page.load_networks()
        elif (
            isinstance(self.current_page, tuple)
            and self.current_page[0] == "network_details"
        ):
            network_id = self.current_page[1]

            from zerotier_gui.utils import state

            state.update_network_cache(network_id, network=None, members=None)

            self.clear_content()
            from .pages.network_details import NetworkDetailsPage

            new_details_page = NetworkDetailsPage(self.app, network_id)
            self.content_box.append(new_details_page)

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

    def show_join_network_page(self):
        from .pages import JoinNetworkPage

        self.clear_content()
        self.current_page = "join_network"

        self.clear_header_actions()

        self.title_label.set_text("Join Network")

        self.back_button.set_visible(True)
        self.header_actions.append(self.back_button)

        join_page = JoinNetworkPage(self.app, self.show_networks_page)
        self.content_box.append(join_page)
        self.sidebar.set_visible(False)

    def show_user_info_page(self, button=None):
        self.clear_content()
        self.current_page = "user_info"

        self.clear_header_actions()

        self.title_label.set_text("User Information")

        user_info_page = UserInfoPage(self.app)
        self.content_box.append(user_info_page)
        self.sidebar.set_visible(False)

    def show_loading_indicator(self, message):
        self.loading_overlay = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.loading_overlay.set_valign(Gtk.Align.CENTER)
        self.loading_overlay.set_halign(Gtk.Align.CENTER)
        self.loading_overlay.add_css_class("loading-overlay")

        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        self.loading_overlay.append(spinner)

        label = Gtk.Label(label=message)
        label.add_css_class("loading-message")
        self.loading_overlay.append(label)

        self.overlay.add_overlay(self.loading_overlay)
        self.loading_overlay.set_visible(True)

    def hide_loading_indicator(self):
        if hasattr(self, "loading_overlay") and self.loading_overlay:
            self.overlay.remove_overlay(self.loading_overlay)
            self.loading_overlay = None

    def show_message_dialog(self, title, message, message_type):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )

        try:
            dialog.set_secondary_text(message)
        except AttributeError:
            dialog.destroy()

            dialog = Gtk.Dialog(
                title=title,
                transient_for=self,
                modal=True,
            )
            dialog.add_button("OK", Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)

            content_area = dialog.get_content_area()
            content_area.set_spacing(12)
            content_area.set_margin_top(12)
            content_area.set_margin_bottom(12)
            content_area.set_margin_start(12)
            content_area.set_margin_end(12)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

            icon_name = "dialog-information-symbolic"
            if message_type == Gtk.MessageType.WARNING:
                icon_name = "dialog-warning-symbolic"
            elif message_type == Gtk.MessageType.ERROR:
                icon_name = "dialog-error-symbolic"
            elif message_type == Gtk.MessageType.QUESTION:
                icon_name = "dialog-question-symbolic"

            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_icon_size(Gtk.IconSize.LARGE)
            hbox.append(icon)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            title_label = Gtk.Label()
            title_label.set_markup(f"<b>{title}</b>")
            title_label.set_halign(Gtk.Align.START)
            vbox.append(title_label)

            msg_label = Gtk.Label(label=message)
            msg_label.set_halign(Gtk.Align.START)
            msg_label.set_wrap(True)
            vbox.append(msg_label)

            hbox.append(vbox)
            content_area.append(hbox)

        dialog.add_css_class("message-dialog")

        button_box = dialog.get_widget_for_response(Gtk.ResponseType.OK)
        if button_box:
            button_box.add_css_class("dialog-button")
            if message_type == Gtk.MessageType.INFO:
                button_box.add_css_class("suggested-action")

        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
