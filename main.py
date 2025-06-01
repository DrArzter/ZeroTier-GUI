import os
import sys
import asyncio
from loguru import logger
from zerotier_gui.utils import check_service, check_root
from zerotier_gui.gui.application import Application
from zerotier_gui import api

logger.remove()
logger.add(sys.stderr, level="ERROR")


async def initialize_app():
    """Initialize the application by loading necessary data."""

    # NOTE: I don't know if i still need this, gonna comment it out for now
    # await check_root()
    # await check_service()

    await api.initialize_user()

    app = Application()
    return app.run()


def main():
    """Entry point for the application."""

    return asyncio.run(initialize_app())


if __name__ == "__main__":
    main()
