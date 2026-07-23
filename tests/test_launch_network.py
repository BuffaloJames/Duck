"""Unit tests for launch_network script."""

from pathlib import Path
import subprocess
from unittest.mock import MagicMock, patch
import pytest

from launch_network import (
    get_local_wifi_ip,
    main,
    start_servers,
    update_django_settings,
    update_frontend_env,
)


class TestLaunchNetwork:
    """Test suite for launch_network script functions."""

    def test_get_local_wifi_ip_success(self) -> None:
        """Test get_local_wifi_ip returns valid IP string."""
        ip = get_local_wifi_ip()
        assert isinstance(ip, str)
        assert len(ip.split(".")) == 4

    @patch("socket.socket")
    def test_get_local_wifi_ip_fallback(self, mock_socket: MagicMock) -> None:
        """Test get_local_wifi_ip handles socket exception with fallback."""
        mock_socket.side_effect = OSError("Socket error")
        ip = get_local_wifi_ip()
        assert isinstance(ip, str)

    def test_update_django_settings_missing_file(self, tmp_path: Path) -> None:
        """Test update_django_settings handles missing settings file gracefully."""
        missing_file = tmp_path / "nonexistent.py"
        res = update_django_settings("192.168.1.100", missing_file)
        assert res is False

    def test_update_django_settings_success(self, tmp_path: Path) -> None:
        """Test update_django_settings updates ALLOWED_HOSTS and CORS in file."""
        settings_file = tmp_path / "settings.py"
        settings_file.write_text('ALLOWED_HOSTS = ["localhost"]\n', encoding="utf-8")

        res = update_django_settings("192.168.1.100", settings_file)
        assert res is True

        content = settings_file.read_text(encoding="utf-8")
        assert "192.168.1.100" in content
        assert "CORS_ALLOW_ALL_ORIGINS = True" in content

    def test_update_django_settings_already_wildcard(self, tmp_path: Path) -> None:
        """Test update_django_settings preserves existing wildcard ALLOWED_HOSTS."""
        settings_file = tmp_path / "settings.py"
        settings_file.write_text('ALLOWED_HOSTS = ["*"]\n', encoding="utf-8")

        res = update_django_settings("192.168.1.100", settings_file)
        assert res is True

    def test_update_frontend_env_success(self, tmp_path: Path) -> None:
        """Test update_frontend_env creates .env.local file with API URL."""
        env_file = tmp_path / ".env.local"
        res = update_frontend_env("192.168.1.100", env_file)
        assert res is True

        content = env_file.read_text(encoding="utf-8")
        assert "VITE_API_BASE_URL=http://192.168.1.100:8000/api" in content

    def test_update_frontend_env_permission_error(self, tmp_path: Path) -> None:
        """Test update_frontend_env handles write permissions error gracefully."""
        invalid_path = tmp_path / "nonexistent_dir" / ".env.local"
        res = update_frontend_env("192.168.1.100", invalid_path)
        assert res is False

    @patch("subprocess.Popen")
    def test_start_servers_success(self, mock_popen: MagicMock, tmp_path: Path) -> None:
        """Test start_servers launches processes cleanly."""
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        d_proc, v_proc = start_servers("192.168.1.100", tmp_path)
        assert d_proc is not None
        assert v_proc is not None
        assert mock_popen.call_count == 2

    @patch("subprocess.Popen")
    def test_start_servers_failure(self, mock_popen: MagicMock, tmp_path: Path) -> None:
        """Test start_servers handles process creation error gracefully."""
        mock_popen.side_effect = subprocess.SubprocessError("Subprocess failed")
        d_proc, v_proc = start_servers("192.168.1.100", tmp_path)
        assert d_proc is None
        assert v_proc is None

    @patch("launch_network.start_servers")
    @patch("launch_network.update_frontend_env")
    @patch("launch_network.update_django_settings")
    @patch("launch_network.get_local_wifi_ip")
    def test_main_execution(
        self,
        mock_ip: MagicMock,
        mock_django: MagicMock,
        mock_env: MagicMock,
        mock_start: MagicMock,
    ) -> None:
        """Test main entry point execution flow."""
        mock_ip.return_value = "192.168.1.100"
        mock_proc1 = MagicMock()
        mock_proc2 = MagicMock()
        mock_start.return_value = (mock_proc1, mock_proc2)

        mock_proc1.wait.side_effect = KeyboardInterrupt()

        main()
        assert mock_ip.called
        assert mock_django.called
        assert mock_env.called
        assert mock_start.called
