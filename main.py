import os
import sys
import asyncio
from loguru import logger
from zerotier_gui.utils import check_service, check_root
from zerotier_gui.gui.application import Application
from zerotier_gui import api

# Configure logging
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="ERROR")  # Add handler only for errors

async def initialize_app():
    """Initialize the application by loading necessary data."""
    # Check permissions and service
    check_root()
    await check_service()
    
    # Initialize user data
    await api.initialize_user()
    
    # Create and run the application
    app = Application()
    return app.run()

def main():
    """Entry point for the application."""
    # Run asynchronous initialization
    return asyncio.run(initialize_app())

if __name__ == "__main__":
    main()
