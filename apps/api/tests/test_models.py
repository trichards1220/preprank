from app.models import Sport, School, Team, Game, PowerRating


def test_sport_table_name():
    assert Sport.__tablename__ == "sports"


def test_school_table_name():
    assert School.__tablename__ == "schools"


def test_team_table_name():
    assert Team.__tablename__ == "teams"


def test_game_table_name():
    assert Game.__tablename__ == "games"


def test_power_rating_table_name():
    assert PowerRating.__tablename__ == "power_ratings"
