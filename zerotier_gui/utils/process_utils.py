import asyncio
import subprocess
import os
import sys
import tempfile
from loguru import logger
from ..decorators import handle_exceptions

@handle_exceptions
async def run_command(cmd, check=True):
    """Run a command asynchronously and return the output.
    
    Args:
        cmd: List of command and arguments
        check: Whether to raise an exception if the command fails
        
    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    stdout_str = stdout.decode('utf-8') if stdout else ""
    stderr_str = stderr.decode('utf-8') if stderr else ""
    
    if check and process.returncode != 0:
        logger.error(f"Command {cmd} failed with code {process.returncode}")
        logger.error(f"STDOUT: {stdout_str}")
        logger.error(f"STDERR: {stderr_str}")
        raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
        
    return stdout_str, stderr_str, process.returncode

@handle_exceptions
async def create_and_run_temp_script(script_content, use_sudo=False):
    """Create a temporary script and run it.
    
    Args:
        script_content: The content of the script to run
        use_sudo: Whether to run the script with sudo
        
    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    try:
        # Create temporary script
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as temp:
            temp.write(script_content)
            script_path = temp.name
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Run script
        cmd = ["pkexec", script_path] if use_sudo else [script_path]
        result = await run_command(cmd)
        
        # Clean up
        os.unlink(script_path)
        
        return result
    except Exception as e:
        logger.exception(f"Error running temporary script: {e}")
        return "", str(e), 1

def open_url_as_user(url):
    """Open a URL using the user's default browser.
    
    This is useful when running as root via pkexec.
    """
    real_uid = os.environ.get('PKEXEC_UID')
    if real_uid:
        try:
            import pwd
            user = pwd.getpwuid(int(real_uid)).pw_name
            
            # Save current environment variables
            display = os.environ.get('DISPLAY', ':0')
            xdg_runtime = f"/run/user/{real_uid}"
            dbus_session = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
            
            # Form command with preserved environment variables
            cmd = [
                'su',
                user,
                '-c',
                f'DISPLAY={display} XDG_RUNTIME_DIR={xdg_runtime} DBUS_SESSION_BUS_ADDRESS={dbus_session} xdg-open {url}'
            ]

            subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
            return True
        except (KeyError, ValueError) as e:
            logger.error(f"Error opening URL as user: {e}")
            return False
    else:
        # Not running as root, just open directly
        try:
            subprocess.Popen(['xdg-open', url], stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            return False 