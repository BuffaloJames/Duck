"""Automated Local Network Launcher for Duck Card Game.

Detects local Wi-Fi IP address, updates Django ALLOWED_HOSTS & CORS configuration,
updates Vite frontend environment variables, and launches both backend and frontend servers
for local network access on macOS and mobile devices.
"""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any, Optional, Tuple


def get_local_wifi_ip() -> str:
    """Retrieve local Wi-Fi IP address dynamically.

    Attempts to connect to an external IP via UDP socket to determine the active
    local Wi-Fi network interface IP address. Degrades gracefully to fallback localhost.

    Returns:
        String representing local IPv4 address (e.g. '192.168.1.50'), or '127.0.0.1'.

    Raises:
        RuntimeError: Handled internally with fallback to '127.0.0.1'.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        # Connect to public DNS address without sending data to find route
        sock.connect(("8.8.8.8", 80))
        ip_address = sock.getsockname()[0]
        sock.close()
        if ip_address and isinstance(ip_address, str):
            return ip_address
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        if ip_address and not ip_address.startswith("127."):
            return ip_address
    except Exception:
        pass

    return "127.0.0.1"


def update_django_settings(ip: str, settings_path: Optional[Path] = None) -> bool:
    """Update Django settings file to include local network IP in ALLOWED_HOSTS and CORS.

    Args:
        ip: Local network IPv4 address string to inject.
        settings_path: Optional Path to Django settings.py file. Defaults to project path.

    Returns:
        True if settings were successfully updated or already configured, False otherwise.

    Raises:
        FileNotFoundError: If settings.py file path does not exist.
        PermissionError: If settings.py is not writable.
    """
    if settings_path is None:
        settings_path = (
            Path(__file__).resolve().parent / "backend" / "duck_project" / "settings.py"
        )

    if not settings_path.exists():
        print(f"Warning: Django settings file not found at {settings_path}")
        return False

    try:
        content = settings_path.read_text(encoding="utf-8")

        modified = False

        # Update ALLOWED_HOSTS
        if f'"{ip}"' not in content and f"'{ip}'" not in content:
            if 'ALLOWED_HOSTS = ["*"]' in content or "ALLOWED_HOSTS = ['*']" in content:
                pass  # Wildcard already allows all
            elif "ALLOWED_HOSTS = [" in content:
                content = content.replace(
                    "ALLOWED_HOSTS = [", f'ALLOWED_HOSTS = ["{ip}", '
                )
                modified = True

        # Ensure CORS is configured for network requests
        if "CORS_ALLOW_ALL_ORIGINS = True" not in content:
            content += "\nCORS_ALLOW_ALL_ORIGINS = True\n"
            modified = True

        if modified:
            settings_path.write_text(content, encoding="utf-8")
            print(f"Updated Django settings for IP: {ip}")
        return True
    except (OSError, IOError, PermissionError) as exc:
        print(f"Failed to update Django settings: {exc}")
        return False


def update_frontend_env(ip: str, env_path: Optional[Path] = None) -> bool:
    """Update or create frontend/.env.local with network backend API URL.

    Args:
        ip: Local network IPv4 address string.
        env_path: Optional Path to frontend/.env.local file.

    Returns:
        True if frontend env file was successfully created/updated, False on error.

    Raises:
        PermissionError: If file is not writable.
    """
    if env_path is None:
        env_path = Path(__file__).resolve().parent / "frontend" / ".env.local"

    api_url = f"http://{ip}:8000/api"
    env_content = f"VITE_API_BASE_URL={api_url}\n"

    try:
        env_path.write_text(env_content, encoding="utf-8")
        print(f"Updated Frontend .env.local with VITE_API_BASE_URL={api_url}")
        return True
    except (OSError, IOError, PermissionError) as exc:
        print(f"Failed to write frontend .env.local: {exc}")
        return False


def start_servers(
    ip: str, base_dir: Optional[Path] = None
) -> Tuple[Optional[subprocess.Popen[Any]], Optional[subprocess.Popen[Any]]]:
    """Launch Django and Vite dev servers for network access using subprocesses.

    Args:
        ip: Local IPv4 address.
        base_dir: Optional base directory path of the repository.

    Returns:
        Tuple containing (Django Popen process, Vite Popen process).

    Raises:
        SubprocessError: Handled gracefully if server launch fails.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent

    django_cmd = [
        sys.executable,
        "manage.py",
        "runserver",
        "0.0.0.0:8000",
    ]
    vite_cmd = ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

    django_proc: Optional[subprocess.Popen[Any]] = None
    vite_proc: Optional[subprocess.Popen[Any]] = None

    try:
        print("Starting Django REST API backend on 0.0.0.0:8000...")
        django_proc = subprocess.Popen(django_cmd, cwd=base_dir)

        frontend_dir = base_dir / "frontend"
        print("Starting Vite React frontend on 0.0.0.0:5173...")
        vite_proc = subprocess.Popen(vite_cmd, cwd=frontend_dir)

        print("\n=======================================================")
        print(f" 🦆 DUCK CARD GAME NETWORK SERVER IS RUNNING!")
        print(f" Access on your iPhone over Wi-Fi at:")
        print(f" 📱 Frontend: http://{ip}:5173")
        print(f" ⚙️ Backend:  http://{ip}:8000/api")
        print(" Press Ctrl+C to stop both servers.")
        print("=======================================================\n")

        return django_proc, vite_proc
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"Error starting servers: {exc}")
        if django_proc:
            django_proc.terminate()
        if vite_proc:
            vite_proc.terminate()
        return None, None


def main() -> None:
    """Main execution function for local network launcher script."""
    ip = get_local_wifi_ip()
    update_django_settings(ip)
    update_frontend_env(ip)
    django_proc, vite_proc = start_servers(ip)

    if django_proc and vite_proc:
        try:
            django_proc.wait()
            vite_proc.wait()
        except KeyboardInterrupt:
            print("\nShutting down servers gracefully...")
            django_proc.terminate()
            vite_proc.terminate()


if __name__ == "__main__":
    main()
