// Matches the FastAPI Pydantic response schemas exactly

export interface Sport {
  id: number;
  name: string;
  season: string;
  has_power_rating: boolean;
}

export interface School {
  id: number;
  name: string;
  city: string | null;
  parish: string | null;
  classification: string | null;
  division: string | null;
  select_status: string | null;
  enrollment: number | null;
  created_at: string | null;
}

export interface SchoolDetail extends School {
  teams: Team[];
}

export interface Team {
  id: number;
  school_id: number;
  sport_id: number;
  season_year: number;
  head_coach: string | null;
  division: string | null;
  select_status: string | null;
}

export interface Game {
  id: number;
  home_team_id: number;
  away_team_id: number;
  sport_id: number;
  season_year: number;
  game_date: string | null;
  week_number: number | null;
  home_score: number | null;
  away_score: number | null;
  status: string;
  is_district: boolean;
  is_playoff: boolean;
  is_championship: boolean;
  is_out_of_state: boolean;
  source: string | null;
}

export interface PowerRating {
  id: number;
  team_id: number;
  week_number: number;
  season_year: number;
  power_rating: number;
  strength_factor: number | null;
  rank_in_division: number | null;
  total_teams_in_division: number | null;
  calculated_at: string | null;
}

export interface ProjectedRating {
  team_id: number;
  projected_rating_mean: number | null;
  projected_rating_median: number | null;
  projected_rating_p10: number | null;
  projected_rating_p90: number | null;
  projected_rank_mean: number | null;
  playoff_probability: number | null;
  championship_probability: number | null;
  projected_wins_mean: number | null;
  projected_losses_mean: number | null;
  made_playoffs: number | null;
  won_round1: number | null;
  reached_quarters: number | null;
  reached_semis: number | null;
  reached_championship: number | null;
  won_title: number | null;
}

export interface WhatsAtStake {
  team_id: number;
  game_id: number;
  opponent_team_id: number;
  opponent_school_name: string | null;
  game_date: string | null;
  week_number: number | null;
  is_home: boolean;
  current_rating: number | null;
  current_rank: number | null;
  projected_rating_if_win: number | null;
  projected_rank_if_win: number | null;
  playoff_prob_if_win: number | null;
  projected_rating_if_loss: number | null;
  projected_rank_if_loss: number | null;
  playoff_prob_if_loss: number | null;
}

export interface StandingEntry {
  team_id: number;
  school_name: string;
  division: string | null;
  select_status: string | null;
  power_rating: number;
  strength_factor: number | null;
  rank_in_division: number | null;
  wins: number | null;
  losses: number | null;
}

export interface Standings {
  sport_id: number;
  season_year: number;
  division: string;
  select_status: string;
  week_number: number;
  standings: StandingEntry[];
}

export interface User {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  subscription_tier: string;
  subscription_expires: string | null;
  created_at: string | null;
}

export interface Favorite {
  id: number;
  entity_type: string;
  entity_id: number;
  created_at: string | null;
}

export interface Notification {
  id: number;
  notification_type: string;
  title: string | null;
  message: string | null;
  game_id: number | null;
  read_status: boolean;
  sent_at: string | null;
}

export interface GameImpact {
  game_id: number;
  affected_team_id: number;
  rating_if_home_wins: number | null;
  rating_if_away_wins: number | null;
  rank_if_home_wins: number | null;
  rank_if_away_wins: number | null;
  playoff_prob_if_home_wins: number | null;
  playoff_prob_if_away_wins: number | null;
}
