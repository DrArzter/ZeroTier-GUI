import os
import sys
import subprocess
import asyncio
from ..decorators import handle_exceptions
from .process_utils import run_command


@handle_exceptions
async def check_service():
    """
    Check if zerotier-one.service is running and try to start it if it's not.
    Returns True if the service is running or was started successfully.
    """
    try:
        if os.geteuid() != 0:
            # Check if zerotier-one.service is running
            _, _, returncode = await run_command(
                ["systemctl", "is-active", "zerotier-one.service"],
                check=False
            )
            
            if returncode != 0:
                # Try to start the service
                await run_command(
                    ["systemctl", "start", "zerotier-one.service"],
                    check=False
                )
                
                # Check if the service started
                _, _, check_returncode = await run_command(
                    ["systemctl", "is-active", "zerotier-one.service"],
                    check=False
                )
                
                if check_returncode != 0:
                    sys.exit(1)
            
            return True
    except Exception:
        return False


def check_root():
    """
    Check if the application is running with root privileges.
    If not, try to restart it with root privileges using pkexec.
    """
    if os.geteuid() != 0:
        try:
            # Get the current user's UID
            real_uid = os.getuid()

            # Get full path to current script
            script_path = os.path.abspath(sys.argv[0])

            # Save necessary environment variables
            env = os.environ.copy()

            # Try to restart application with root privileges via pkexec
            cmd = [
                "pkexec",
                "env",
                f'DISPLAY={env.get("DISPLAY", ":0")}',
                f'XAUTHORITY={env.get("XAUTHORITY", "")}',
                f'DBUS_SESSION_BUS_ADDRESS={env.get("DBUS_SESSION_BUS_ADDRESS", "")}',
                f"PKEXEC_UID={real_uid}",  # Pass the real user's UID
                f"XDG_RUNTIME_DIR=/run/user/{real_uid}",  # Pass the XDG runtime dir
                f'HOME={os.path.expanduser("~")}',  # Pass the real user's home
                sys.executable,
                script_path,
            ]
            subprocess.run(cmd, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError:
            sys.exit(1)
