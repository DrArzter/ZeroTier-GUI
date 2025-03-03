import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from .networks import NetworksPage
from .about import AboutPage

class SettingsPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label="Settings Page (Coming Soon)")
        self.append(label)

__all__ = ['NetworksPage', 'SettingsPage', 'AboutPage'] 