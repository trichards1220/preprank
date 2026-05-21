from app.schemas.schools import SchoolOut
from app.schemas.teams import TeamOut
from app.schemas.ratings import PowerRatingOut, RankedTeamOut


def test_school_out_schema():
    s = SchoolOut(
        id=1, name="Ruston", city=None, parish=None,
        classification="5A", division="I", select_status="Non-Select",
        enrollment=None
    )
    assert s.name == "Ruston"
    assert s.classification == "5A"


def test_team_out_schema():
    t = TeamOut(
        id=1, school_id=1, sport_id=1, season_year=2025,
        head_coach=None, division="I", select_status="Non-Select",
        school_name="Ruston", sport_name="Football"
    )
    assert t.school_name == "Ruston"


def test_power_rating_out_schema():
    r = PowerRatingOut(
        id=1, team_id=1, week_number=11, season_year=2025,
        power_rating=14.40, strength_factor=11.40,
        rank_in_division=1, total_teams_in_division=64
    )
    assert float(r.power_rating) == 14.40


def test_ranked_team_out_schema():
    rt = RankedTeamOut(
        rank=1, school_name="Ruston", division="I",
        classification="5A", select_status="Non-Select",
        power_rating=14.40, strength_factor=11.40,
        team_id=1, school_id=1
    )
    assert rt.rank == 1
    assert rt.school_name == "Ruston"
