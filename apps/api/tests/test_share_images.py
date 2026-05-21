"""Share image generation tests."""
from app.services.share_images import (
    generate_team_card, generate_game_card,
    generate_pickem_results_card, generate_school_leaderboard_card,
    generate_badge_card,
)


def test_team_card_is_png():
    data = generate_team_card("Ruston", 14.4, 1, "I", "5A")
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert len(data) > 1000


def test_game_card_is_png():
    data = generate_game_card("Ruston", "Neville", 14.4, 14.2)
    assert data[:8] == b'\x89PNG\r\n\x1a\n'


def test_pickem_results_card():
    data = generate_pickem_results_card("Test U.", 8, 10, "St. Paul's", "Sharp Eye", 5)
    assert data[:8] == b'\x89PNG\r\n\x1a\n'


def test_leaderboard_card():
    data = generate_school_leaderboard_card("St. Paul's", 1, 45, 50, 12)
    assert data[:8] == b'\x89PNG\r\n\x1a\n'


def test_badge_card():
    data = generate_badge_card("Test U.", "Perfect Week", "All 10 correct")
    assert data[:8] == b'\x89PNG\r\n\x1a\n'


def test_team_card_dimensions():
    from PIL import Image
    from io import BytesIO
    data = generate_team_card("Ruston", 14.4, 1, "I", "5A")
    img = Image.open(BytesIO(data))
    assert img.size == (1200, 630)
