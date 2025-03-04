import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def create_page_header(title: str, with_refresh_button=True, app=None, on_refresh=None):
    """Creates a standard page header with an optional refresh button."""
    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    header_box.set_margin_bottom(16)
    
    # Page title
    page_title = Gtk.Label()
    page_title.set_markup(f"<span size='x-large' weight='bold'>{title}</span>")
    page_title.set_halign(Gtk.Align.START)
    header_box.append(page_title)
    
    # Empty expanding element
    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    header_box.append(spacer)
    
    # Refresh button
    if with_refresh_button and app and on_refresh:
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text(f"Refresh {title}")
        refresh_btn.connect("clicked", on_refresh)
        header_box.append(refresh_btn)
    
    return header_box

def create_info_section(title: str, items: list, is_first_section=False):
    """Creates an information section (used in network_details and user_info)."""
    # Container for the entire section
    section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    
    # Section header
    section_label = Gtk.Label()
    section_label.set_markup(f"<span size='large' weight='bold'>{title}</span>")
    section_label.set_halign(Gtk.Align.START)
    section_label.set_xalign(0.0)
    
    # Margins
    section_label.set_margin_top(0 if is_first_section else 8)
    section_label.set_margin_bottom(4)
    section_label.add_css_class("network-info-section-title")
    section_box.append(section_label)
    
    # Container for items
    items_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    items_box.add_css_class("network-info-section")
    items_box.set_hexpand(True)
    items_box.set_halign(Gtk.Align.FILL)
    
    # Add items
    for label, value in items:
        item_box = create_info_row(label, value)
        items_box.append(item_box)
    
    section_box.append(items_box)
    return section_box

def create_info_row(label: str, value: str):
    """Creates an information row (label: value)."""
    item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    item_box.add_css_class("network-info-row")
    item_box.set_hexpand(True)
    item_box.set_halign(Gtk.Align.FILL)
    
    # Label
    label_widget = Gtk.Label()
    label_widget.set_markup(f"<b>{label}:</b>")
    label_widget.set_halign(Gtk.Align.START)
    label_widget.set_xalign(0.0)
    label_widget.set_size_request(150, -1)
    label_widget.add_css_class("network-info-label")
    item_box.append(label_widget)
    
    # Value
    value_widget = Gtk.Label(label=str(value))
    value_widget.set_halign(Gtk.Align.END)
    value_widget.set_hexpand(True)
    value_widget.set_wrap(True)
    value_widget.set_selectable(True)
    value_widget.set_xalign(1.0)
    value_widget.set_yalign(0.0)
    value_widget.add_css_class("network-info-value")
    item_box.append(value_widget)
    
    return item_box

def create_loading_overlay(message: str):
    """Creates an overlay with a loading indicator."""
    overlay = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    overlay.set_valign(Gtk.Align.CENTER)
    overlay.set_halign(Gtk.Align.CENTER)
    overlay.add_css_class("loading-overlay")
    
    # Spinner
    spinner = Gtk.Spinner()
    spinner.set_size_request(32, 32)
    spinner.start()
    overlay.append(spinner)
    
    # Message
    label = Gtk.Label(label=message)
    label.add_css_class("loading-message")
    overlay.append(label)
    
    return overlay

def show_status_message(label_widget: Gtk.Label, message: str, is_error=False, is_success=False):
    """Shows a status message with the appropriate style."""
    label_widget.set_text(message)
    
    # Remove all CSS classes
    label_widget.remove_css_class("error-message")
    label_widget.remove_css_class("success-message")
    
    # Add the appropriate CSS class
    if is_error:
        label_widget.add_css_class("error-message")
    elif is_success:
        label_widget.add_css_class("success-message")
    
    label_widget.set_visible(True)

def create_scrollable_container():
    """Creates a scrollable container with hidden scrollbars."""
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.add_css_class("hidden-scrollbar")
    return scroll

def create_page_container(css_class="app-page"):
    """Creates a standard page container with appropriate CSS classes."""
    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    container.add_css_class(css_class)
    return container

def create_action_button(icon_name=None, label=None, tooltip=None):
    """Creates an action button with either an icon or a label."""
    button = Gtk.Button()
    
    if icon_name:
        button.set_icon_name(icon_name)
    elif label:
        button.set_label(label)
        
    if tooltip:
        button.set_tooltip_text(tooltip)
        
    return button

def create_list_row_container():
    """Creates a standard container for list rows."""
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    box.add_css_class("list-row-box")
    return box

def create_list_row_info():
    """Creates a standard info container for list rows."""
    info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    info_box.add_css_class("list-row-info")
    return info_box 