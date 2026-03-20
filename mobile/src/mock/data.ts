import type {
  Sport, School, SchoolDetail, Team, Game, PowerRating, ProjectedRating,
  WhatsAtStake, StandingEntry, Standings, User, Favorite, Notification,
  PickemContest, PickemSlate, PickemPick, PickemLeaderboardEntry,
  SchoolLeaderboardEntry, HypeScore, BadgeInfo, UserBadge,
} from '../types/api';

// ── Sports ──────────────────────────────────────────────────
export const mockSports: Sport[] = [
  { id: 1, name: 'Football', season: 'fall', has_power_rating: true },
  { id: 2, name: 'Volleyball', season: 'fall', has_power_rating: true },
  { id: 3, name: 'Cross Country', season: 'fall', has_power_rating: false },
  { id: 4, name: 'Boys Basketball', season: 'winter', has_power_rating: true },
  { id: 5, name: 'Girls Basketball', season: 'winter', has_power_rating: true },
  { id: 6, name: 'Wrestling', season: 'winter', has_power_rating: false },
  { id: 7, name: 'Baseball', season: 'spring', has_power_rating: true },
  { id: 8, name: 'Softball', season: 'spring', has_power_rating: true },
  { id: 9, name: 'Boys Soccer', season: 'spring', has_power_rating: true },
  { id: 10, name: 'Girls Soccer', season: 'spring', has_power_rating: true },
  { id: 11, name: 'Tennis', season: 'spring', has_power_rating: false },
  { id: 12, name: 'Golf', season: 'spring', has_power_rating: false },
  { id: 13, name: 'Outdoor Track and Field', season: 'spring', has_power_rating: false },
  { id: 14, name: 'Indoor Track and Field', season: 'winter', has_power_rating: false },
  { id: 15, name: 'Swimming', season: 'fall', has_power_rating: false },
  { id: 16, name: 'Bowling', season: 'winter', has_power_rating: false },
  { id: 17, name: 'Gymnastics', season: 'winter', has_power_rating: false },
  { id: 18, name: 'Boys Golf', season: 'spring', has_power_rating: false },
  { id: 19, name: 'Girls Golf', season: 'spring', has_power_rating: false },
  { id: 20, name: 'Boys Tennis', season: 'spring', has_power_rating: false },
  { id: 21, name: 'Girls Tennis', season: 'spring', has_power_rating: false },
  { id: 22, name: 'Boys Swimming', season: 'fall', has_power_rating: false },
  { id: 23, name: 'Girls Swimming', season: 'fall', has_power_rating: false },
];

// ── Schools ─────────────────────────────────────────────────
export const mockSchools: School[] = [
  { id: 1, name: 'Ruston', city: 'Ruston', parish: 'Lincoln', classification: '5A', division: 'I', select_status: 'Non-Select', enrollment: 1200, created_at: null },
  { id: 2, name: 'Neville', city: 'Monroe', parish: 'Ouachita', classification: '5A', division: 'I', select_status: 'Non-Select', enrollment: 900, created_at: null },
  { id: 3, name: 'Edna Karr', city: 'New Orleans', parish: 'Orleans', classification: '4A', division: 'I', select_status: 'Select', enrollment: 800, created_at: null },
  { id: 4, name: 'Destrehan', city: 'Destrehan', parish: 'St. Charles', classification: '5A', division: 'I', select_status: 'Non-Select', enrollment: 1500, created_at: null },
  { id: 5, name: 'Lafayette Christian', city: 'Lafayette', parish: 'Lafayette', classification: '2A', division: 'III', select_status: 'Select', enrollment: 400, created_at: null },
  { id: 6, name: 'West Monroe', city: 'West Monroe', parish: 'Ouachita', classification: '5A', division: 'I', select_status: 'Non-Select', enrollment: 1100, created_at: null },
  { id: 7, name: 'St. Augustine', city: 'New Orleans', parish: 'Orleans', classification: '4A', division: 'I', select_status: 'Select', enrollment: 750, created_at: null },
  { id: 8, name: 'Zachary', city: 'Zachary', parish: 'East Baton Rouge', classification: '5A', division: 'I', select_status: 'Non-Select', enrollment: 1300, created_at: null },
];

// ── Teams ───────────────────────────────────────────────────
export const mockTeams: Team[] = [
  { id: 1, school_id: 1, sport_id: 1, season_year: 2025, head_coach: 'Jerrod Baugh', division: 'I', select_status: 'Non-Select' },
  { id: 2, school_id: 2, sport_id: 1, season_year: 2025, head_coach: 'Jeff Tannehill', division: 'I', select_status: 'Non-Select' },
  { id: 3, school_id: 3, sport_id: 1, season_year: 2025, head_coach: 'Brice Brown', division: 'I', select_status: 'Select' },
  { id: 4, school_id: 4, sport_id: 1, season_year: 2025, head_coach: 'Marcus Scott', division: 'I', select_status: 'Non-Select' },
  { id: 5, school_id: 5, sport_id: 1, season_year: 2025, head_coach: 'Trev Faulk', division: 'III', select_status: 'Select' },
  { id: 6, school_id: 6, sport_id: 1, season_year: 2025, head_coach: 'Jerry Arledge', division: 'I', select_status: 'Non-Select' },
  { id: 7, school_id: 7, sport_id: 1, season_year: 2025, head_coach: 'Nathaniel Jones', division: 'I', select_status: 'Select' },
  { id: 8, school_id: 8, sport_id: 1, season_year: 2025, head_coach: 'David Brewerton', division: 'I', select_status: 'Non-Select' },
];

// ── Games (Ruston schedule) ─────────────────────────────────
export const mockGames: Game[] = [
  { id: 1, home_team_id: 101, away_team_id: 1, sport_id: 1, season_year: 2025, game_date: '2025-09-05', week_number: 1, home_score: 7, away_score: 49, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 2, home_team_id: 1, away_team_id: 102, sport_id: 1, season_year: 2025, game_date: '2025-09-12', week_number: 2, home_score: 63, away_score: 28, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: true, source: 'lhsaa' },
  { id: 3, home_team_id: 1, away_team_id: 103, sport_id: 1, season_year: 2025, game_date: '2025-09-19', week_number: 3, home_score: 38, away_score: 35, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: true, source: 'lhsaa' },
  { id: 10, home_team_id: 1, away_team_id: 2, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: 49, away_score: 44, status: 'final', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 11, home_team_id: 1, away_team_id: 50, sport_id: 1, season_year: 2025, game_date: '2025-11-14', week_number: null, home_score: null, away_score: null, status: 'scheduled', is_district: false, is_playoff: true, is_championship: false, is_out_of_state: false, source: null },
];

// ── Pick'em Slate Games ─────────────────────────────────────
export const mockPickemSlateGames: Game[] = [
  { id: 201, home_team_id: 1, away_team_id: 6, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
  { id: 202, home_team_id: 3, away_team_id: 7, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
  { id: 203, home_team_id: 2, away_team_id: 4, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
  { id: 204, home_team_id: 5, away_team_id: 8, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
  { id: 205, home_team_id: 110, away_team_id: 111, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: 35, away_score: 28, status: 'final', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 206, home_team_id: 112, away_team_id: 113, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: 14, away_score: 21, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 207, home_team_id: 114, away_team_id: 115, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
  { id: 208, home_team_id: 116, away_team_id: 117, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: null, away_score: null, status: 'scheduled', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: null },
];

// Pick'em friendly labels for slate games (home vs away school names)
export const mockPickemSlateLabels: Record<number, { home: string; away: string }> = {
  201: { home: 'Ruston', away: 'West Monroe' },
  202: { home: 'Edna Karr', away: 'St. Augustine' },
  203: { home: 'Neville', away: 'Destrehan' },
  204: { home: 'Lafayette Christian', away: 'Zachary' },
  205: { home: 'Parkway', away: 'Northwood' },
  206: { home: 'Central - B.R.', away: 'Denham Springs' },
  207: { home: 'Catholic - B.R.', away: 'Teurlings Catholic' },
  208: { home: 'Southside', away: 'Comeaux' },
};

// ── Power Ratings ───────────────────────────────────────────
export const mockPowerRatings: PowerRating[] = [
  { id: 1, team_id: 1, week_number: 10, season_year: 2025, power_rating: 14.40, strength_factor: 11.40, rank_in_division: 1, total_teams_in_division: 41, calculated_at: '2025-11-08T12:00:00' },
  { id: 2, team_id: 2, week_number: 10, season_year: 2025, power_rating: 14.20, strength_factor: 11.60, rank_in_division: 2, total_teams_in_division: 41, calculated_at: '2025-11-08T12:00:00' },
  { id: 3, team_id: 3, week_number: 10, season_year: 2025, power_rating: 15.82, strength_factor: 10.50, rank_in_division: 1, total_teams_in_division: 36, calculated_at: '2025-11-08T12:00:00' },
  { id: 4, team_id: 4, week_number: 10, season_year: 2025, power_rating: 14.00, strength_factor: 11.00, rank_in_division: 3, total_teams_in_division: 41, calculated_at: '2025-11-08T12:00:00' },
  { id: 5, team_id: 5, week_number: 10, season_year: 2025, power_rating: 17.70, strength_factor: 10.10, rank_in_division: 1, total_teams_in_division: 35, calculated_at: '2025-11-08T12:00:00' },
];

// ── Projections ─────────────────────────────────────────────
export const mockProjections: Record<number, ProjectedRating> = {
  1: { team_id: 1, projected_rating_mean: 14.52, projected_rating_median: 14.50, projected_rating_p10: 13.80, projected_rating_p90: 15.20, projected_rank_mean: 1.4, playoff_probability: 100, championship_probability: 18.5, projected_wins_mean: 9.2, projected_losses_mean: 2.8, made_playoffs: 100, won_round1: 94.2, reached_quarters: 78.5, reached_semis: 52.1, reached_championship: 28.4, won_title: 18.5 },
  2: { team_id: 2, projected_rating_mean: 14.10, projected_rating_median: 14.05, projected_rating_p10: 13.20, projected_rating_p90: 14.90, projected_rank_mean: 2.8, playoff_probability: 100, championship_probability: 12.3, projected_wins_mean: 8.5, projected_losses_mean: 3.5, made_playoffs: 100, won_round1: 88.7, reached_quarters: 65.2, reached_semis: 41.8, reached_championship: 22.1, won_title: 12.3 },
  3: { team_id: 3, projected_rating_mean: 15.90, projected_rating_median: 15.88, projected_rating_p10: 15.20, projected_rating_p90: 16.60, projected_rank_mean: 1.1, playoff_probability: 100, championship_probability: 32.7, projected_wins_mean: 11.4, projected_losses_mean: 0.6, made_playoffs: 100, won_round1: 98.9, reached_quarters: 92.4, reached_semis: 71.3, reached_championship: 45.6, won_title: 32.7 },
};

// ── What's At Stake ─────────────────────────────────────────
export const mockWhatsAtStake: WhatsAtStake = {
  team_id: 1,
  game_id: 11,
  opponent_team_id: 50,
  opponent_school_name: 'Zachary',
  game_date: '2025-11-14',
  week_number: null,
  is_home: true,
  current_rating: 14.40,
  current_rank: 1,
  projected_rating_if_win: 14.82,
  projected_rank_if_win: 1,
  playoff_prob_if_win: 100,
  projected_rating_if_loss: 13.90,
  projected_rank_if_loss: 3,
  playoff_prob_if_loss: 100,
};

// ── Standings ───────────────────────────────────────────────
export const mockStandings: Standings[] = [
  {
    sport_id: 1, season_year: 2025, division: 'I', select_status: 'Non-Select', week_number: 10,
    standings: [
      { team_id: 1, school_name: 'Ruston', division: 'I', select_status: 'Non-Select', power_rating: 14.40, strength_factor: 11.40, rank_in_division: 1, wins: 8, losses: 2 },
      { team_id: 2, school_name: 'Neville', division: 'I', select_status: 'Non-Select', power_rating: 14.20, strength_factor: 11.60, rank_in_division: 2, wins: 7, losses: 3 },
      { team_id: 4, school_name: 'Destrehan', division: 'I', select_status: 'Non-Select', power_rating: 14.00, strength_factor: 11.00, rank_in_division: 3, wins: 8, losses: 2 },
      { team_id: 10, school_name: 'Denham Springs', division: 'I', select_status: 'Non-Select', power_rating: 13.39, strength_factor: 9.90, rank_in_division: 4, wins: 8, losses: 2 },
      { team_id: 11, school_name: 'Central - B.R.', division: 'I', select_status: 'Non-Select', power_rating: 13.32, strength_factor: 9.60, rank_in_division: 5, wins: 8, losses: 2 },
      { team_id: 12, school_name: 'Parkway', division: 'I', select_status: 'Non-Select', power_rating: 13.24, strength_factor: 8.90, rank_in_division: 6, wins: 9, losses: 1 },
      { team_id: 13, school_name: 'Northwood - Shrev.', division: 'I', select_status: 'Non-Select', power_rating: 13.16, strength_factor: 9.00, rank_in_division: 7, wins: 8, losses: 2 },
      { team_id: 14, school_name: 'Southside', division: 'I', select_status: 'Non-Select', power_rating: 13.10, strength_factor: 9.50, rank_in_division: 8, wins: 8, losses: 2 },
    ],
  },
  {
    sport_id: 1, season_year: 2025, division: 'I', select_status: 'Select', week_number: 10,
    standings: [
      { team_id: 3, school_name: 'Edna Karr', division: 'I', select_status: 'Select', power_rating: 15.82, strength_factor: 10.50, rank_in_division: 1, wins: 10, losses: 0 },
      { team_id: 20, school_name: 'Teurlings Catholic', division: 'I', select_status: 'Select', power_rating: 14.83, strength_factor: 8.80, rank_in_division: 2, wins: 10, losses: 0 },
      { team_id: 21, school_name: 'St. Augustine', division: 'I', select_status: 'Select', power_rating: 14.58, strength_factor: 10.10, rank_in_division: 3, wins: 9, losses: 1 },
      { team_id: 22, school_name: 'Catholic - B.R.', division: 'I', select_status: 'Select', power_rating: 14.47, strength_factor: 10.90, rank_in_division: 4, wins: 8, losses: 1 },
    ],
  },
];

// ── User ────────────────────────────────────────────────────
export const mockUser: User = {
  id: 1,
  email: 'thomas@teamtitle.com',
  first_name: 'Thomas',
  last_name: 'Richards',
  subscription_tier: 'annual',
  subscription_expires: '2027-03-20T00:00:00',
  created_at: '2026-03-20T00:00:00',
};

// ── Favorites ───────────────────────────────────────────────
export const mockFavorites: Favorite[] = [
  { id: 1, entity_type: 'team', entity_id: 1, created_at: '2026-03-20T00:00:00' },
  { id: 2, entity_type: 'team', entity_id: 3, created_at: '2026-03-20T00:00:00' },
  { id: 3, entity_type: 'team', entity_id: 5, created_at: '2026-03-20T00:00:00' },
];

// ── Notifications ───────────────────────────────────────────
export const mockNotifications: Notification[] = [
  { id: 1, notification_type: 'ranking_change', title: 'Ruston climbs to #1', message: 'Ruston moved from #3 to #1 in Division I Non-Select after beating West Monroe 49-44.', game_id: 10, read_status: false, sent_at: '2025-11-07T22:30:00' },
  { id: 2, notification_type: 'prediction_update', title: 'Playoff path update', message: 'Edna Karr\'s title probability increased to 32.7% after St. Augustine lost to Catholic-BR.', game_id: null, read_status: false, sent_at: '2025-11-07T21:15:00' },
  { id: 3, notification_type: 'score_update', title: 'Final: Lafayette Christian 42, Notre Dame 28', message: 'Lafayette Christian clinched the Division III Select top seed with a 42-28 win.', game_id: 50, read_status: true, sent_at: '2025-11-07T21:00:00' },
  { id: 4, notification_type: 'game_reminder', title: 'Tomorrow: Ruston vs Zachary', message: 'First round playoff matchup. Ruston hosts Zachary at 7:00 PM. If Ruston wins, projected rating rises to 14.82.', game_id: 11, read_status: true, sent_at: '2025-11-13T10:00:00' },
];

// ── Pick'em ─────────────────────────────────────────────────
export const mockPickemContest: PickemContest = {
  id: 1,
  sport_id: 1,
  season_year: 2025,
  week_number: 10,
  name: 'Week 10 Football Pick\'em',
  status: 'active',
};

export const mockPickemSlates: PickemSlate[] = [
  { id: 1, contest_id: 1, game_id: 201 },
  { id: 2, contest_id: 1, game_id: 202 },
  { id: 3, contest_id: 1, game_id: 203 },
  { id: 4, contest_id: 1, game_id: 204 },
  { id: 5, contest_id: 1, game_id: 205 },
  { id: 6, contest_id: 1, game_id: 206 },
  { id: 7, contest_id: 1, game_id: 207 },
  { id: 8, contest_id: 1, game_id: 208 },
];

export const mockPickemPicks: PickemPick[] = [
  { id: 1, slate_id: 1, game_id: 201, picked_winner_team_id: 1, is_correct: null, points_earned: 0, picked_at: '2025-11-06T14:30:00' },
  { id: 2, slate_id: 2, game_id: 202, picked_winner_team_id: 3, is_correct: null, points_earned: 0, picked_at: '2025-11-06T14:31:00' },
  { id: 3, slate_id: 3, game_id: 203, picked_winner_team_id: 2, is_correct: null, points_earned: 0, picked_at: '2025-11-06T14:32:00' },
  { id: 4, slate_id: 5, game_id: 205, picked_winner_team_id: 110, is_correct: true, points_earned: 10, picked_at: '2025-11-06T14:33:00' },
  { id: 5, slate_id: 6, game_id: 206, picked_winner_team_id: 112, is_correct: false, points_earned: 0, picked_at: '2025-11-06T14:34:00' },
];

export const mockPickemLeaderboard: PickemLeaderboardEntry[] = [
  { user_id: 42, school_name: 'Ruston', total_points: 185, correct_picks: 72, upset_picks: 8, rank: 1, streak: 6 },
  { user_id: 17, school_name: 'Neville', total_points: 170, correct_picks: 68, upset_picks: 6, rank: 2, streak: 3 },
  { user_id: 1, school_name: 'Ruston', total_points: 162, correct_picks: 65, upset_picks: 5, rank: 3, streak: 4 },
  { user_id: 88, school_name: 'Edna Karr', total_points: 155, correct_picks: 61, upset_picks: 7, rank: 4, streak: 2 },
  { user_id: 33, school_name: 'Destrehan', total_points: 148, correct_picks: 58, upset_picks: 4, rank: 5, streak: 1 },
  { user_id: 55, school_name: 'West Monroe', total_points: 140, correct_picks: 55, upset_picks: 3, rank: 6, streak: 0 },
  { user_id: 71, school_name: 'St. Augustine', total_points: 135, correct_picks: 52, upset_picks: 5, rank: 7, streak: 2 },
  { user_id: 29, school_name: 'Lafayette Christian', total_points: 128, correct_picks: 50, upset_picks: 2, rank: 8, streak: 1 },
  { user_id: 64, school_name: 'Zachary', total_points: 120, correct_picks: 47, upset_picks: 3, rank: 9, streak: 0 },
  { user_id: 91, school_name: 'Catholic - B.R.', total_points: 115, correct_picks: 45, upset_picks: 1, rank: 10, streak: 1 },
];

export const mockSchoolLeaderboard: SchoolLeaderboardEntry[] = [
  { school_id: 1, school_name: 'Ruston', total_points: 1240, avg_accuracy: 72.5, participant_count: 45 },
  { school_id: 3, school_name: 'Edna Karr', total_points: 1180, avg_accuracy: 70.2, participant_count: 38 },
  { school_id: 2, school_name: 'Neville', total_points: 1050, avg_accuracy: 68.8, participant_count: 32 },
  { school_id: 4, school_name: 'Destrehan', total_points: 980, avg_accuracy: 66.1, participant_count: 28 },
  { school_id: 6, school_name: 'West Monroe', total_points: 920, avg_accuracy: 64.5, participant_count: 25 },
];

// ── Hype Scores ─────────────────────────────────────────────
export const mockHypeScores: HypeScore[] = [
  { team_id: 1, week_number: 10, season_year: 2025, hype_score: 8.5, momentum_direction: 'rising', win_streak: 4, rating_change_4wk: 1.2 },
  { team_id: 2, week_number: 10, season_year: 2025, hype_score: 7.2, momentum_direction: 'steady', win_streak: 1, rating_change_4wk: -0.3 },
  { team_id: 6, week_number: 10, season_year: 2025, hype_score: 6.1, momentum_direction: 'falling', win_streak: 0, rating_change_4wk: -1.8 },
  { team_id: 3, week_number: 10, season_year: 2025, hype_score: 9.4, momentum_direction: 'rising', win_streak: 10, rating_change_4wk: 0.6 },
];

// ── Badges ──────────────────────────────────────────────────
export const mockBadges: BadgeInfo[] = [
  { id: 1, name: 'Upset Caller', description: 'Correctly predicted 3 upsets in a single season', icon: 'flame', rarity: 'rare', criteria_type: 'upset_picks' },
  { id: 2, name: 'Oracle', description: 'Achieved 80%+ accuracy over 10 consecutive weeks', icon: 'eye', rarity: 'legendary', criteria_type: 'accuracy_streak' },
  { id: 3, name: 'District Expert', description: 'Correctly picked all district games in a week', icon: 'map', rarity: 'uncommon', criteria_type: 'district_sweep' },
  { id: 4, name: 'Iron Pick', description: 'Made picks for every game in 8 consecutive weeks', icon: 'shield-checkmark', rarity: 'rare', criteria_type: 'consistency' },
  { id: 5, name: 'Crystal Ball', description: 'Predicted the state champion before the playoffs began', icon: 'diamond', rarity: 'legendary', criteria_type: 'champion_prediction' },
  { id: 6, name: 'First Pick', description: 'Made your very first pick on PrepRank', icon: 'flag', rarity: 'common', criteria_type: 'first_pick' },
];

export const mockUserBadges: UserBadge[] = [
  { id: 1, badge_id: 1, badge_name: 'Upset Caller', badge_icon: 'flame', badge_rarity: 'rare', earned_at: '2025-10-15T18:00:00', description: 'Correctly predicted 3 upsets in a single season' },
  { id: 2, badge_id: 6, badge_name: 'First Pick', badge_icon: 'flag', badge_rarity: 'common', earned_at: '2025-09-05T12:00:00', description: 'Made your very first pick on PrepRank' },
  { id: 3, badge_id: 3, badge_name: 'District Expert', badge_icon: 'map', badge_rarity: 'uncommon', earned_at: '2025-10-28T21:30:00', description: 'Correctly picked all district games in a week' },
];

// ── Helper: resolve school name for a team ──────────────────
export function schoolNameForTeam(teamId: number): string {
  const team = mockTeams.find(t => t.id === teamId);
  if (!team) return 'Unknown';
  const school = mockSchools.find(s => s.id === team.school_id);
  return school?.name ?? 'Unknown';
}

export function powerRatingForTeam(teamId: number): PowerRating | undefined {
  return mockPowerRatings.find(pr => pr.team_id === teamId);
}
