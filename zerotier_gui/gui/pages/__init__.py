import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from .networks import NetworksPage
from .about import AboutPage
from .join_network import JoinNetworkPage
from .user_info import UserInfoPage

class SettingsPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.add_css_class("app-page")
        label = Gtk.Label(label="Settings Page (Coming Soon)")
        self.append(label)

__all__ = ['NetworksPage', 'SettingsPage', 'AboutPage', 'JoinNetworkPage', 'UserInfoPage'] 