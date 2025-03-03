import os
import sys
import subprocess
from zerotier_gui.gui.application import Application

def check_root():
    if os.geteuid() != 0:
        try:
            # Get the current user's UID
            real_uid = os.getuid()
            
            # Get full path to current script
            script_path = os.path.abspath(__file__)
            
            # Save necessary environment variables
            env = os.environ.copy()
            
            # Try to restart application with root privileges via pkexec
            cmd = [
                'pkexec',
                'env',
                f'DISPLAY={env.get("DISPLAY", ":0")}',
                f'XAUTHORITY={env.get("XAUTHORITY", "")}',
                f'DBUS_SESSION_BUS_ADDRESS={env.get("DBUS_SESSION_BUS_ADDRESS", "")}',
                f'PKEXEC_UID={real_uid}',  # Pass the real user's UID
                f'XDG_RUNTIME_DIR=/run/user/{real_uid}',  # Pass the XDG runtime dir
                f'HOME={os.path.expanduser("~")}',  # Pass the real user's home
                sys.executable,
                script_path
            ]
            subprocess.run(cmd, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Error: This application requires root privileges.")
            sys.exit(1)

def main():
    check_root()
    app = Application()
    return app.run()

if __name__ == "__main__":
    main()
