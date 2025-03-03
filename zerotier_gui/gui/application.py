import gi
import asyncio
from loguru import logger
from .window import MainWindow

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.gtk.ZeroTierGUI")
        self.connect("activate", self.on_activate)
        self.window = None
        
        # Создаем event loop в отдельном потоке
        self.loop = asyncio.new_event_loop()
        import threading
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_activate(self, app):
        if not self.window:
            self.window = MainWindow(application=app, app=self)
        self.window.present()

    def run_async(self, coro):
        if not self.loop:
            logger.error("Event loop not initialized")
            return None
            
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        
        def done_callback(fut):
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Async error: {e}")
                
        future.add_done_callback(done_callback)
        return future 