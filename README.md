# PrepRank — Louisiana High School Sports Power Ranking Predictor
## Project Brief & Technical Blueprint
### Last Updated: March 20, 2026

---

## 1. PRODUCT OVERVIEW

PrepRank is a subscription-based web and mobile application that tracks LHSAA (Louisiana High School Athletic Association) power rankings across all 23 sanctioned sports and predicts how upcoming game outcomes will affect each team's power ranking and playoff positioning.

### Core Differentiator
The predictive engine. No competitor (GeauxPreps, MaxPreps, LHSAA Live, ScoreStream) offers forward-looking analysis. PrepRank answers the question every coach, parent, and fan asks: **"What's at stake in Friday night's game?"**

### Key Insight About the LHSAA Power Rating System
The LHSAA power rating has a **retroactive dependency**. When you beat Team X in Week 3, the value of that win changes every subsequent week as Team X plays more games. The opponent wins component (Team X's wins / total games × 10) recalculates continuously. This means predicting the impact of any single game requires predicting the probable outcome of **every remaining game on every opponent's schedule, and every game on those opponents' opponents' schedules**. It's a fully coupled network. This complexity is the technical moat.

---

## 2. LHSAA POWER RATING FORMULA

### Football (Primary — other sports use similar formulas)
For each game played:
- **Result Points**: Win = 10 points, Loss = 0 points
- **Play-Up Points**: If opponent is in a higher division & class, +2 points per division & class higher (based on playoff division, not classification — changed April 2023)
- **Opponent Wins Points**: (Opponent's wins / Opponent's total games played) × 10

**Game Power Points** = Result + Play-Up + Opponent Wins
**Season Power Rating** = Total Power Points across all games / Number of games played (rounded to nearest hundredth)

### Tiebreaker (Strength Factor)
(Sum of opponents' class + Sum of opponents' wins) / Total number of games played

### Key Rules
- Power ratings updated every 4 hours by GeauxPreps; LHSAA publishes final Week 10 ratings as PDFs
- JV and "B" team games are NOT included in power rating calculations
- Out-of-state opponents' classification is determined by verifying enrollment through their state association
- Minimum game requirements vary by sport (e.g., softball requires at least 15 regular season games for playoff eligibility)

---

## 3. DATA SOURCES & STRATEGY

### Primary Target: LHSAA Direct Partnership
- **lhsaaonline.org** is the centralized member portal where all game results are entered
- Home team coaches are REQUIRED to enter scores (fined $50 per missed report)
- Opposing coaches confirm or dispute results
- Data is verified, complete, and authoritative across all sports/classifications
- **Contact: Kathie Smith (ksmith@lhsaa.org), Eddie Bonine (Executive Director)**
- The portal is built and maintained by **GenTech Software, Inc.** (Louisiana company)

### Secondary: LHSAA Published Data (Public, No License Needed)
- Final power rating PDFs published on lhsaa.org for each sport season
- Playoff brackets archived back to 2002 (football), 2003+ (other sports)
- General information bulletins with schedules, classifications, and rules
- **Available PDFs confirmed**: 2022, 2023, 2024, 2025 football power ratings (Select & Non-Select)

### Tertiary: ScoreStream API (Licensed, Real-Time)
- Crowdsourced scores, 10,000-15,000 high school games/week nationally
- Louisiana is listed among their largest state communities
- Covers football, basketball, baseball, softball, soccer, volleyball
- **Contact: partner@scorestream.com** for API pricing (estimated $500-2,000/month)
- Coverage may be incomplete for smaller schools/non-football sports

### Supplementary: MaxPreps (Public Pages)
- Complete schedule and score data viewable without subscription
- Coaches voluntarily enter stats (not guaranteed complete)
- GameChanger syncs automatically for baseball/softball
- **Terms of Service prohibit commercial scraping** — use for validation only

### LHSAA Live App (Intelligence Only)
- Official LHSAA consumer app built by **Sporting Innovations** (package: com.sportinginnovations.omslhsaa)
- Sporting Innovations builds identical white-label apps for multiple state associations (Oregon OSAA, etc.)
- The app consumes an API that already exposes scores, schedules, stats — this API exists and could potentially be licensed from Sporting Innovations
- **Sporting Innovations is a potential data licensing partner**

### LHSAA Ecosystem Connections
- **PlayOn Sports** owns NFHS Network (streaming), MaxPreps (stats), GoFan (ticketing) — stats flow automatically from NFHS cameras to MaxPreps
- **Arbiter** handles officials scheduling and student athlete registration for LHSAA
- **NFHS Network** streams LHSAA championship events

---

## 4. LHSAA LEGAL STATUS

- **Private nonprofit corporation** (EIN: 72-0513180)
- Louisiana Supreme Court ruled LHSAA is NOT a public/quasi-public entity (Louisiana High School Athletic Association, Inc. v. State, 2012-1471, La. 1/29/13)
- NOT subject to Open Meetings Law or Public Records Law
- Contracts with vendors are PRIVATE — not accessible via procurement databases
- Files IRS Form 990 annually (public document — check ProPublica Nonprofit Explorer)
- Form 990 Part VII Section B lists top 5 independent contractors paid >$100K
- ~400 member schools, ~93,000 student athletes, ~12,000 coaches

---

## 5. COMPETITIVE LANDSCAPE

### GeauxPreps (Direct Competitor)
- **Pricing**: $9.99/month or $99/year (no free tier)
- **Estimated subscribers**: 1,000-3,000 (based on ~11,500 monthly unique visitors)
- **Strengths**: Trusted brand, power ratings updated every 4 hours, editorial content, CCS podcast
- **Weaknesses**: Website only (no native app), no predictive features, no push notifications, high price for basic data
- **Key person**: William Weathers (primary contributor), Vincent Cacioppo (managing editor)

### MaxPreps (National Player)
- Free with ads, some premium features behind paywall
- Massive national database but Louisiana-specific depth is limited
- No LHSAA power rating calculations
- No predictive features

### LHSAA Live App
- Free, official LHSAA app
- Basic scores, schedules, news
- Poor reviews ("Does nothing, slower than dial up")
- No power ratings, no predictions

### Louisiana Sportsline
- Message boards, power ratings via Google Sheets
- Community-driven, not a polished product

---

## 6. TARGET MARKET & PRICING

### Total Addressable Market (Louisiana)
- Student athletes: ~93,000
- Parents/family (2 per athlete): ~186,000
- Coaches and staff: ~12,000
- Dedicated fans/boosters/alumni: ~50,000-100,000
- **Total realistic market: ~300,000-400,000 potential users**
- **Conversion target: 5-10% = 15,000-40,000 paid subscribers at maturity**

### Pricing Structure
| Tier | Price | What's Included |
|------|-------|----------------|
| **Free** | $0 | Current scores, schedules, basic standings, current week power ratings |
| **Premium Monthly** | $5.99/mo | Predictive engine, projected final power ratings, "what's at stake" previews, My Athletes, push notifications, historical trends |
| **Season Pass** | $24.99 | Single sport season (4-5 months) — captures football-only crowd |
| **Annual** | $49.99 | All sports, all year — positioned as "less than $1/week" |

### Revenue Projections
- 5,000 subscribers (Year 1 conservative): ~$200K
- 10,000 subscribers: ~$400K
- 20,000 subscribers (maturity): ~$800K

---

## 7. TECHNICAL ARCHITECTURE

### Tech Stack
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Frontend (Web)**: React or Next.js
- **Mobile**: React Native (cross-platform iOS + Android)
- **Prediction Engine**: Python (NumPy/SciPy for Monte Carlo simulations)
- **Push Notifications**: Firebase Cloud Messaging
- **Hosting**: AWS (or GCP)
- **CI/CD**: GitHub Actions

### Infrastructure Estimates
| Component | Spec | Monthly Cost |
|-----------|------|-------------|
| API/Backend Server | AWS t3.large or equivalent | $60-80 |
| Database | PostgreSQL on RDS db.t3.medium | $50-70 |
| Monte Carlo Compute | Burst c5.2xlarge (spin up/down) | $50-100 |
| Push Notifications | Firebase FCM | Free |
| CDN/Static Hosting | CloudFront | $20-30 |
| **Total at Launch** | | **$300-500/month** |
| **Total at Scale (25K+ users)** | | **$800-1,500/month** |

### App Store Costs
- Apple Developer Program: $99/year
- Google Play: $25 one-time

---

## 8. PREDICTION ENGINE — MONTE CARLO SIMULATION

### How It Works
1. Take every remaining game in the season across the entire state
2. Assign a win probability to each game based on available inputs
3. Simulate the entire rest of the season 10,000 times
4. Each simulation produces complete final records for every team
5. Calculate exact power ratings for every team in each simulation
6. Aggregate across all simulations to produce probability distributions

### Output for Users
"If your team wins Friday, you have a 78% chance of finishing in the top 8 and making playoffs. If you lose, that drops to 31%."

### Prediction Input Tiers
| Tier | Inputs | Accuracy Level |
|------|--------|---------------|
| **Tier 1 (Launch)** | Wins, losses, scores, schedule, classification, home/away, power rating network math | Functional |
| **Tier 2 (Post-Launch)** | + Point differentials (margin of victory), + strength of schedule depth | Significantly better |
| **Tier 3 (Aspirational)** | + Player stats, injuries, weather, user-contributed data | Elite |

### Compute Requirements
- ~400 member schools, ~200-300 games per week (football)
- 10,000 Monte Carlo runs × ~10 remaining weeks = ~30 million game simulations per weekly update
- Executes in minutes on a modern cloud instance
- Basketball/baseball have more games but same math — just more iterations

### Key Technical Note
The LHSAA does NOT require coaches to report game statistics — only scores. Individual player stats are voluntary and entered via MaxPreps/GameChanger by coaches who choose to participate. The "My Athletes" feature could create a user-contributed stats flywheel over time.

---

## 9. USER EXPERIENCE

### Home Screen
- **My Athletes** / **My Teams** dashboard
- Current power ratings, next game, projected finish, recent changes

### Navigation Path
Sport → Classification → Division → Team → Schedule/Roster/Power Rating detail

### Team Detail View
- Current power rating
- Projected final power rating (with confidence range from Monte Carlo)
- Schedule with results and upcoming games
- For each upcoming game: "What's at stake" breakdown showing projected power rating impact of win vs loss

### Athlete Detail View
- Stats (where available), team affiliation, schedule
- Parent engagement hook — follow your kid's team and see personalized updates

### Push Notifications
- Not just "your team won" — **"Rummel just lost to Jesuit, which moved your team from 12th to 9th in projected playoff seeding"**
- Any game result that impacts a followed team's power rating triggers a notification
- Configurable by user (team-level, sport-level, or all)

---

## 10. DEVELOPMENT TIMELINE

| Phase | Dates | Deliverables |
|-------|-------|-------------|
| **Architecture & Data** | Now - April | Database schema, power rating engine, scraping scripts, historical test data |
| **Prediction Engine** | April - May | Monte Carlo simulation, win probability model, validation against historical data |
| **Backend API** | May - June | FastAPI endpoints, user auth, subscription management, push notification pipeline |
| **Frontend & Mobile** | May - July | React Native app, web app, UI/UX |
| **Infrastructure** | Late June - July | AWS provisioning, CI/CD, App Store submissions |
| **Beta Testing** | Late July | Invite-only testing with coaches and booster club members |
| **Public Launch** | August | Coincide with football jamboree week / fall sports kickoff |
| **Marketing Push** | June - August | PR, social media, coaching clinics, local media outreach |

---

## 11. DATABASE SCHEMA (High-Level)

### Core Tables
- **schools** — id, name, city, parish, classification, division, select_status, enrollment, lhsaa_member_id
- **sports** — id, name, season (fall/winter/spring), has_power_rating (boolean)
- **teams** — id, school_id, sport_id, season_year, head_coach
- **games** — id, home_team_id, away_team_id, sport_id, game_date, home_score, away_score, status (scheduled/final/disputed), is_district, is_playoff, week_number
- **power_ratings** — id, team_id, week_number, season_year, power_rating, strength_factor, rank_in_division, calculated_at
- **athletes** — id, school_id, name, graduation_year, position, jersey_number
- **athlete_stats** — id, athlete_id, game_id, stat_type, stat_value

### User/Subscription Tables
- **users** — id, email, password_hash, subscription_tier, subscription_expires, created_at
- **user_favorites** — id, user_id, entity_type (team/athlete), entity_id
- **notifications** — id, user_id, type, message, game_id, read_status, sent_at

### Prediction Tables
- **simulations** — id, sport_id, season_year, week_number, run_count, completed_at
- **projected_ratings** — id, simulation_id, team_id, projected_rating_mean, projected_rating_p10, projected_rating_p90, playoff_probability, projected_rank
- **game_predictions** — id, game_id, simulation_id, home_win_probability, predicted_home_score, predicted_away_score

---

## 12. IMMEDIATE NEXT STEPS

1. **Create GitHub repo** (`preprank`) with this brief as README
2. **Build power rating calculation engine** in Python matching exact LHSAA formula
3. **Pull historical test data** — scrape LHSAA 2023-2025 football power rating PDFs, extract and structure into PostgreSQL seed data
4. **Validate engine** against known final power ratings from past seasons
5. **Build Monte Carlo simulation framework**
6. **Contact LHSAA** (Kathie Smith, Eddie Bonine) about data partnership
7. **Contact Sporting Innovations** about data licensing
8. **Contact ScoreStream** (partner@scorestream.com) about API access/pricing
9. **Pull LHSAA Form 990** from ProPublica (EIN 720513180) to map vendor ecosystem

---

## 13. KEY CONTACTS

| Entity | Contact | Purpose |
|--------|---------|---------|
| LHSAA Operations | Kathie Smith, ksmith@lhsaa.org | Data partnership, API access |
| LHSAA Executive Director | Eddie Bonine | Strategic partnership |
| GenTech Software | (Built lhsaaonline.org) | Technical API development |
| Sporting Innovations | (Built LHSAA Live app) | Data licensing |
| ScoreStream | partner@scorestream.com | Real-time score API |
| GeauxPreps | hbower@geauxpreps.com | Competitive intelligence |

---

## 14. OPEN QUESTIONS TO RESOLVE

- [ ] LHSAA data partnership — will they grant API access?
- [ ] LHSAA Form 990 — who are their current technology vendors and what are they paying?
- [ ] ScoreStream API pricing — what's the actual cost for Louisiana-only high school data?
- [ ] Sporting Innovations — will they license the LHSAA Live API separately?
- [ ] App name — "PrepRank" is a working title; final name TBD
- [ ] Branding, logo, color scheme
- [ ] Legal entity for the app business
- [ ] Privacy policy and terms of service (COPPA considerations for minor athletes)
