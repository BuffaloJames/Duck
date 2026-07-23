"""Unit and integration tests for Django REST API endpoints."""

import json
import pytest
from django.test import Client


@pytest.mark.django_db
class TestDuckApiEndpoints:
    """Test suite for Duck REST API views."""

    def setup_method(self) -> None:
        """Set up Django test client."""
        self.client = Client()

    def test_create_game_session(self) -> None:
        """Test POST /api/game/new/ creates game session and returns state."""
        response = self.client.post(
            "/api/game/new/",
            data=json.dumps(
                {"player_count": 4, "player_name": "TestUser", "difficulty": "Medium"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()

        assert "session_id" in data
        assert data["current_round"] == 1
        assert data["hand_size"] == 7
        assert len(data["players"]) == 4
        assert data["players"][0]["name"] == "TestUser"

    def test_create_game_invalid_player_count(self) -> None:
        """Test error handling when player count is out of range."""
        response = self.client.post(
            "/api/game/new/",
            data=json.dumps({"player_count": 10}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.json()

    def test_step_ai_endpoint(self) -> None:
        """Test POST /api/game/<id>/step_ai/ endpoint."""
        create_resp = self.client.post(
            "/api/game/new/",
            data=json.dumps({"player_count": 3, "player_name": "Alice"}),
            content_type="application/json",
        )
        session_id = create_resp.json()["session_id"]

        step_resp = self.client.post(f"/api/game/{session_id}/step_ai/")
        assert step_resp.status_code == 200
        assert "ai_stepped" in step_resp.json()

    def test_get_nonexistent_session(self) -> None:
        """Test GET request for missing session returns 404."""
        response = self.client.get("/api/game/nonexistent-session-id/")
        assert response.status_code == 404
