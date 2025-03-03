import os
from gi.repository import Gtk
from .kde_colors import KDEColorManager

def load_css(window):
    kde_colors = KDEColorManager()
    kde_colors.apply_to_window(window) 