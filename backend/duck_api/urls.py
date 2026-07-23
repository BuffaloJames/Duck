"""URL routes for duck_api REST endpoints."""

from django.urls import path
from backend.duck_api import views

urlpatterns = [
    path("game/new/", views.create_game_view, name="create_game"),
    path("game/<str:session_id>/", views.game_detail_view, name="game_detail"),
    path("game/<str:session_id>/bid/", views.submit_bid_view, name="submit_bid"),
    path("game/<str:session_id>/play/", views.play_card_view, name="play_card"),
    path("game/<str:session_id>/step_ai/", views.step_ai_view, name="step_ai"),
    path(
        "game/<str:session_id>/next_round/",
        views.advance_round_view,
        name="advance_round",
    ),
]
