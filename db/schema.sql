-- PrepRank Database Schema
-- PostgreSQL
-- Last Updated: March 20, 2026

-- ============================================
-- CORE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS sports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL CHECK (season IN ('fall', 'winter', 'spring')),
    has_power_rating BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    parish VARCHAR(100),
    classification VARCHAR(10), -- 5A, 4A, 3A, 2A, 1A
    division VARCHAR(10), -- I, II, III, IV
    select_status VARCHAR(20) CHECK (select_status IN ('Select', 'Non-Select')),
    enrollment INTEGER,
    lhsaa_member_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id),
    sport_id INTEGER REFERENCES sports(id),
    season_year INTEGER NOT NULL,
    head_coach VARCHAR(200),
    division VARCHAR(10),
    select_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(school_id, sport_id, season_year)
);

CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    sport_id INTEGER REFERENCES sports(id),
    season_year INTEGER NOT NULL,
    game_date DATE,
    week_number INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'final', 'disputed', 'cancelled', 'forfeit')),
    is_district BOOLEAN DEFAULT FALSE,
    is_playoff BOOLEAN DEFAULT FALSE,
    is_championship BOOLEAN DEFAULT FALSE,
    is_out_of_state BOOLEAN DEFAULT FALSE,
    source VARCHAR(50), -- 'lhsaa', 'scorestream', 'maxpreps', 'user'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS power_ratings (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    week_number INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    power_rating DECIMAL(6,2) NOT NULL,
    strength_factor DECIMAL(6,2),
    rank_in_division INTEGER,
    total_teams_in_division INTEGER,
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, week_number, season_year)
);

-- ============================================
-- ATHLETE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS athletes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    graduation_year INTEGER,
    position VARCHAR(50),
    jersey_number VARCHAR(10),
    height VARCHAR(10),
    weight INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS athlete_stats (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER REFERENCES athletes(id),
    game_id INTEGER REFERENCES games(id),
    stat_type VARCHAR(50) NOT NULL, -- 'rushing_yards', 'passing_yards', 'touchdowns', etc.
    stat_value DECIMAL(10,2) NOT NULL,
    source VARCHAR(50), -- 'maxpreps', 'gamechanger', 'user', 'coach'
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- USER / SUBSCRIPTION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium_monthly', 'season_pass', 'annual')),
    subscription_expires TIMESTAMP,
    stripe_customer_id VARCHAR(100),
    push_token VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('team', 'athlete', 'school')),
    entity_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, entity_type, entity_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL, -- 'score_update', 'ranking_change', 'game_reminder', 'prediction_update'
    title VARCHAR(200),
    message TEXT,
    game_id INTEGER REFERENCES games(id),
    read_status BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PREDICTION / SIMULATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER REFERENCES sports(id),
    season_year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    run_count INTEGER DEFAULT 10000,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projected_ratings (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id),
    projected_rating_mean DECIMAL(6,2),
    projected_rating_median DECIMAL(6,2),
    projected_rating_p10 DECIMAL(6,2), -- 10th percentile (pessimistic)
    projected_rating_p90 DECIMAL(6,2), -- 90th percentile (optimistic)
    projected_rank_mean DECIMAL(6,1),
    playoff_probability DECIMAL(5,2), -- percentage 0-100
    championship_probability DECIMAL(5,2),
    projected_wins_mean DECIMAL(4,1),
    projected_losses_mean DECIMAL(4,1),
    -- Playoff round advancement probabilities (percentage 0-100)
    made_playoffs DECIMAL(5,2),
    won_round1 DECIMAL(5,2),
    reached_quarters DECIMAL(5,2),
    reached_semis DECIMAL(5,2),
    reached_championship DECIMAL(5,2),
    won_title DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS game_predictions (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    home_win_probability DECIMAL(5,2), -- percentage 0-100
    predicted_home_score DECIMAL(5,1),
    predicted_away_score DECIMAL(5,1),
    predicted_spread DECIMAL(5,1),
    -- Impact analysis: what happens to followed team's rating in each scenario
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS game_impact_analysis (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    simulation_id INTEGER REFERENCES simulations(id) ON DELETE CASCADE,
    affected_team_id INTEGER REFERENCES teams(id), -- the team whose rating is affected
    rating_if_home_wins DECIMAL(6,2),
    rating_if_away_wins DECIMAL(6,2),
    rank_if_home_wins INTEGER,
    rank_if_away_wins INTEGER,
    playoff_prob_if_home_wins DECIMAL(5,2),
    playoff_prob_if_away_wins DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_games_season ON games(season_year, sport_id);
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_power_ratings_team ON power_ratings(team_id, season_year);
CREATE INDEX idx_power_ratings_week ON power_ratings(week_number, season_year);
CREATE INDEX idx_teams_school_sport ON teams(school_id, sport_id, season_year);
CREATE INDEX idx_user_favorites_user ON user_favorites(user_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, read_status);
CREATE INDEX idx_projected_ratings_sim ON projected_ratings(simulation_id);
CREATE INDEX idx_projected_ratings_team ON projected_ratings(team_id);
CREATE INDEX idx_game_predictions_game ON game_predictions(game_id);
CREATE INDEX idx_game_impact_game ON game_impact_analysis(game_id, affected_team_id);

-- ============================================
-- SEED DATA: SPORTS
-- ============================================

INSERT INTO sports (name, season, has_power_rating) VALUES
    ('Football', 'fall', TRUE),
    ('Volleyball', 'fall', TRUE),
    ('Cross Country', 'fall', FALSE),
    ('Swimming', 'fall', FALSE),
    ('Boys Basketball', 'winter', TRUE),
    ('Girls Basketball', 'winter', TRUE),
    ('Wrestling', 'winter', FALSE),
    ('Bowling', 'winter', FALSE),
    ('Indoor Track and Field', 'winter', FALSE),
    ('Gymnastics', 'winter', FALSE),
    ('Baseball', 'spring', TRUE),
    ('Softball', 'spring', TRUE),
    ('Boys Soccer', 'spring', TRUE),
    ('Girls Soccer', 'spring', TRUE),
    ('Tennis', 'spring', FALSE),
    ('Golf', 'spring', FALSE),
    ('Outdoor Track and Field', 'spring', FALSE),
    ('Boys Golf', 'spring', FALSE),
    ('Girls Golf', 'spring', FALSE),
    ('Boys Tennis', 'spring', FALSE),
    ('Girls Tennis', 'spring', FALSE),
    ('Boys Swimming', 'fall', FALSE),
    ('Girls Swimming', 'fall', FALSE)
ON CONFLICT DO NOTHING;
