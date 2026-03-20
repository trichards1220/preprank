import type {
  Sport, School, SchoolDetail, Team, Game, PowerRating, ProjectedRating,
  WhatsAtStake, StandingEntry, Standings, User, Favorite, Notification,
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
];

// ── Teams ───────────────────────────────────────────────────
export const mockTeams: Team[] = [
  { id: 1, school_id: 1, sport_id: 1, season_year: 2025, head_coach: 'Jerrod Baugh', division: 'I', select_status: 'Non-Select' },
  { id: 2, school_id: 2, sport_id: 1, season_year: 2025, head_coach: 'Jeff Tannehill', division: 'I', select_status: 'Non-Select' },
  { id: 3, school_id: 3, sport_id: 1, season_year: 2025, head_coach: 'Brice Brown', division: 'I', select_status: 'Select' },
  { id: 4, school_id: 4, sport_id: 1, season_year: 2025, head_coach: 'Marcus Scott', division: 'I', select_status: 'Non-Select' },
  { id: 5, school_id: 5, sport_id: 1, season_year: 2025, head_coach: 'Trev Faulk', division: 'III', select_status: 'Select' },
];

// ── Games (Ruston schedule) ─────────────────────────────────
export const mockGames: Game[] = [
  { id: 1, home_team_id: 101, away_team_id: 1, sport_id: 1, season_year: 2025, game_date: '2025-09-05', week_number: 1, home_score: 7, away_score: 49, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 2, home_team_id: 1, away_team_id: 102, sport_id: 1, season_year: 2025, game_date: '2025-09-12', week_number: 2, home_score: 63, away_score: 28, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: true, source: 'lhsaa' },
  { id: 3, home_team_id: 1, away_team_id: 103, sport_id: 1, season_year: 2025, game_date: '2025-09-19', week_number: 3, home_score: 38, away_score: 35, status: 'final', is_district: false, is_playoff: false, is_championship: false, is_out_of_state: true, source: 'lhsaa' },
  { id: 10, home_team_id: 1, away_team_id: 2, sport_id: 1, season_year: 2025, game_date: '2025-11-07', week_number: 10, home_score: 49, away_score: 44, status: 'final', is_district: true, is_playoff: false, is_championship: false, is_out_of_state: false, source: 'lhsaa' },
  { id: 11, home_team_id: 1, away_team_id: 50, sport_id: 1, season_year: 2025, game_date: '2025-11-14', week_number: null, home_score: null, away_score: null, status: 'scheduled', is_district: false, is_playoff: true, is_championship: false, is_out_of_state: false, source: null },
];

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
