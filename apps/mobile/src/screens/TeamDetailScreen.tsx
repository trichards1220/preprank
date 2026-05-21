import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import PowerRatingBadge from '../components/PowerRatingBadge';
import WhatsAtStakeCard from '../components/WhatsAtStakeCard';
import HypeCard from '../components/HypeCard';
import {
  mockTeams, mockSchools, mockPowerRatings, mockProjections,
  mockGames, mockWhatsAtStake, mockHypeScores,
} from '../mock/data';

export default function TeamDetailScreen({ route, navigation }: any) {
  const { teamId } = route.params;
  const team = mockTeams.find(t => t.id === teamId);
  const school = team ? mockSchools.find(s => s.id === team.school_id) : null;
  const pr = mockPowerRatings.find(p => p.team_id === teamId);
  const proj = mockProjections[teamId];
  const games = mockGames.filter(g => g.home_team_id === teamId || g.away_team_id === teamId);
  const stake = mockWhatsAtStake.team_id === teamId ? mockWhatsAtStake : null;
  const hype = mockHypeScores.find(h => h.team_id === teamId);

  if (!team || !school) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>Team not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerInfo}>
          <Text style={styles.schoolName}>{school.name}</Text>
          <Text style={styles.meta}>
            Div {team.division} · {team.select_status} · {team.season_year}
          </Text>
          {team.head_coach && (
            <Text style={styles.coach}>Coach {team.head_coach}</Text>
          )}
        </View>
        {pr && <PowerRatingBadge rating={pr.power_rating} rank={pr.rank_in_division} />}
      </View>

      {/* School link */}
      <TouchableOpacity
        style={styles.schoolLink}
        onPress={() => navigation.navigate('SchoolDetail', { schoolId: school.id })}
      >
        <Ionicons name="school-outline" size={16} color={colors.silver} />
        <Text style={styles.schoolLinkText}>View all {school.name} teams</Text>
        <Ionicons name="chevron-forward" size={14} color={colors.textMuted} />
      </TouchableOpacity>

      {/* Hype Score */}
      {hype && (
        <>
          <Text style={styles.sectionTitle}>HYPE SCORE</Text>
          <HypeCard hype={hype} />
        </>
      )}

      {/* Projected Rating */}
      {proj && (
        <>
          <Text style={styles.sectionTitle}>PROJECTED FINISH</Text>
          <View style={styles.projCard}>
            <View style={styles.projMainRow}>
              <View style={styles.projCenter}>
                <Text style={styles.projRating}>{proj.projected_rating_mean?.toFixed(2)}</Text>
                <Text style={styles.projRatingLabel}>Projected Rating</Text>
              </View>
              <View style={styles.projRange}>
                <Text style={styles.rangeLabel}>Confidence Range</Text>
                <Text style={styles.rangeValue}>
                  {proj.projected_rating_p10?.toFixed(2)} — {proj.projected_rating_p90?.toFixed(2)}
                </Text>
              </View>
            </View>
            <View style={styles.projGrid}>
              <ProjStat label="Proj. Rank" value={`#${proj.projected_rank_mean?.toFixed(1)}`} />
              <ProjStat label="Playoffs" value={`${proj.playoff_probability}%`} color={colors.winGreen} />
              <ProjStat label="Win Title" value={`${proj.won_title}%`} />
              <ProjStat label="Proj. W-L" value={`${proj.projected_wins_mean}-${proj.projected_losses_mean}`} />
            </View>

            <Text style={styles.playoffPathTitle}>PLAYOFF PATH</Text>
            <View style={styles.playoffPath}>
              <PathStep label="Make Playoffs" pct={proj.made_playoffs} />
              <PathStep label="Win Round 1" pct={proj.won_round1} />
              <PathStep label="Quarters" pct={proj.reached_quarters} />
              <PathStep label="Semis" pct={proj.reached_semis} />
              <PathStep label="Championship" pct={proj.reached_championship} />
              <PathStep label="Win Title" pct={proj.won_title} highlight />
            </View>
          </View>
        </>
      )}

      {/* What's At Stake */}
      {stake && (
        <>
          <Text style={styles.sectionTitle}>NEXT GAME</Text>
          <WhatsAtStakeCard stake={stake} />
        </>
      )}

      {/* Schedule */}
      <Text style={styles.sectionTitle}>SCHEDULE & RESULTS</Text>
      {games.map(game => {
        const isHome = game.home_team_id === teamId;
        const isFinal = game.status === 'final';
        const teamScore = isHome ? game.home_score : game.away_score;
        const oppScore = isHome ? game.away_score : game.home_score;
        const won = teamScore != null && oppScore != null && teamScore > oppScore;

        return (
          <View key={game.id} style={styles.gameRow}>
            <View style={styles.gameWeek}>
              <Text style={styles.gameWeekText}>
                {game.week_number ? `W${game.week_number}` : 'PO'}
              </Text>
            </View>
            <View style={styles.gameInfo}>
              <Text style={styles.gameOpponent}>
                {isHome ? 'vs' : '@'} {isHome ? `Team #${game.away_team_id}` : `Team #${game.home_team_id}`}
              </Text>
              <Text style={styles.gameDate}>
                {game.game_date ? new Date(game.game_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'TBD'}
                {game.is_district && ' · District'}
                {game.is_playoff && ' · Playoff'}
              </Text>
            </View>
            {isFinal ? (
              <View style={styles.gameScore}>
                <Text style={[styles.gameResult, { color: won ? colors.winGreen : colors.lossRed }]}>
                  {won ? 'W' : 'L'}
                </Text>
                <Text style={styles.gameScoreText}>{teamScore}-{oppScore}</Text>
              </View>
            ) : (
              <Text style={styles.gameScheduled}>
                {game.game_date ? new Date(game.game_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : 'TBD'}
              </Text>
            )}
          </View>
        );
      })}
    </ScrollView>
  );
}

function ProjStat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <View style={pStyles.stat}>
      <Text style={pStyles.statLabel}>{label}</Text>
      <Text style={[pStyles.statValue, color ? { color } : null]}>{value}</Text>
    </View>
  );
}

function PathStep({ label, pct, highlight }: { label: string; pct: number | null; highlight?: boolean }) {
  const width = `${Math.min(pct ?? 0, 100)}%`;
  return (
    <View style={pStyles.pathRow}>
      <Text style={pStyles.pathLabel}>{label}</Text>
      <View style={pStyles.pathBarBg}>
        <View style={[pStyles.pathBarFill, { width: width as any }, highlight && pStyles.pathBarHighlight]} />
      </View>
      <Text style={[pStyles.pathPct, highlight && { color: colors.crimson }]}>
        {pct?.toFixed(1)}%
      </Text>
    </View>
  );
}

const pStyles = StyleSheet.create({
  stat: { width: '25%', alignItems: 'center' },
  statLabel: { color: colors.textMuted, fontSize: fontSize.xs, marginBottom: 2 },
  statValue: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  pathRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.sm },
  pathLabel: { color: colors.silver, fontSize: fontSize.xs, width: 90 },
  pathBarBg: { flex: 1, height: 6, backgroundColor: colors.charcoal, borderRadius: 3, marginHorizontal: spacing.sm },
  pathBarFill: { height: 6, backgroundColor: colors.winGreen, borderRadius: 3 },
  pathBarHighlight: { backgroundColor: colors.crimson },
  pathPct: { color: colors.silver, fontSize: fontSize.xs, width: 45, textAlign: 'right' },
});

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  emptyText: { color: colors.textMuted, fontSize: fontSize.md, textAlign: 'center', marginTop: spacing.xxl },
  header: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: spacing.md },
  headerInfo: { flex: 1 },
  schoolName: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  meta: { color: colors.silver, fontSize: fontSize.sm, marginTop: 4 },
  coach: { color: colors.textMuted, fontSize: fontSize.sm, marginTop: 2 },
  schoolLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.card,
    borderRadius: 8,
    padding: spacing.sm,
    marginBottom: spacing.lg,
  },
  schoolLinkText: { color: colors.silver, fontSize: fontSize.sm, flex: 1 },
  sectionTitle: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  projCard: { backgroundColor: colors.card, borderRadius: 12, padding: spacing.md, borderWidth: 1, borderColor: colors.border },
  projMainRow: { flexDirection: 'row', marginBottom: spacing.md },
  projCenter: { flex: 1 },
  projRating: { color: colors.white, fontSize: fontSize.hero, fontWeight: '800' },
  projRatingLabel: { color: colors.textMuted, fontSize: fontSize.xs },
  projRange: { justifyContent: 'center', alignItems: 'flex-end' },
  rangeLabel: { color: colors.textMuted, fontSize: fontSize.xs },
  rangeValue: { color: colors.silver, fontSize: fontSize.sm, fontWeight: '600' },
  projGrid: {
    flexDirection: 'row',
    paddingVertical: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    marginBottom: spacing.md,
  },
  playoffPathTitle: { color: colors.crimson, fontSize: fontSize.xs, fontWeight: '800', letterSpacing: 2, marginBottom: spacing.md },
  playoffPath: {},
  gameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  gameWeek: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: colors.cardElevated,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  gameWeekText: { color: colors.silver, fontSize: fontSize.xs, fontWeight: '700' },
  gameInfo: { flex: 1 },
  gameOpponent: { color: colors.white, fontSize: fontSize.md, fontWeight: '600' },
  gameDate: { color: colors.textMuted, fontSize: fontSize.xs, marginTop: 2 },
  gameScore: { alignItems: 'flex-end' },
  gameResult: { fontSize: fontSize.md, fontWeight: '800' },
  gameScoreText: { color: colors.silver, fontSize: fontSize.sm },
  gameScheduled: { color: colors.silver, fontSize: fontSize.sm },
});
