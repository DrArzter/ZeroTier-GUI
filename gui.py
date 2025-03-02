import gi
import api

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.gtk.Example")
        self.connect("activate", self.on_activate)
        self.window = None

    def on_activate(self, app):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=app)
            self.window.set_default_size(600, 400)
            self.window.set_title("ZeroTier GUI")

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            self.window.set_child(box)

            button = Gtk.Button(label="Fetch Networks")
            button.connect("clicked", api.get_networks)
            box.append(button)

            label = Gtk.Label(label="Networks:")
            box.append(label)

            network_list = Gtk.ListBox()
            box.append(network_list)

            button = Gtk.Button(label="Fetch Members")
            button.connect("clicked", api.get_network_members)
            box.append(button)

            label = Gtk.Label(label="Members:")
            box.append(label)

            member_list = Gtk.ListBox()
            box.append(member_list)

        self.window.present()


def main():
    app = Application()
    return app.run()


if __name__ == "__main__":
    main()
