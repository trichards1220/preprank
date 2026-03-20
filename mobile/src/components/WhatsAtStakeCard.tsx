import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import type { WhatsAtStake } from '../types/api';

interface Props {
  stake: WhatsAtStake;
}

function ScenarioColumn({ label, rating, rank, playoffProb, color }: {
  label: string;
  rating: number | null;
  rank: number | null;
  playoffProb: number | null;
  color: string;
}) {
  return (
    <View style={styles.scenario}>
      <Text style={[styles.scenarioLabel, { color }]}>{label}</Text>
      <Text style={[styles.scenarioRating, { color }]}>
        {rating?.toFixed(2) ?? '—'}
      </Text>
      <Text style={styles.scenarioDetail}>
        Rank: #{rank ?? '—'}
      </Text>
      <Text style={styles.scenarioDetail}>
        Playoffs: {playoffProb != null ? `${playoffProb}%` : '—'}
      </Text>
    </View>
  );
}

export default function WhatsAtStakeCard({ stake }: Props) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.headerLabel}>WHAT'S AT STAKE</Text>
        <Text style={styles.opponent}>
          {stake.is_home ? 'vs' : '@'} {stake.opponent_school_name}
        </Text>
        {stake.game_date && (
          <Text style={styles.date}>
            {new Date(stake.game_date).toLocaleDateString('en-US', {
              weekday: 'short', month: 'short', day: 'numeric',
            })}
          </Text>
        )}
      </View>

      <View style={styles.currentRow}>
        <Text style={styles.currentLabel}>Current</Text>
        <Text style={styles.currentRating}>{stake.current_rating?.toFixed(2)}</Text>
        <Text style={styles.currentRank}>#{stake.current_rank}</Text>
      </View>

      <View style={styles.scenariosRow}>
        <ScenarioColumn
          label="IF WIN"
          rating={stake.projected_rating_if_win}
          rank={stake.projected_rank_if_win}
          playoffProb={stake.playoff_prob_if_win}
          color={colors.winGreen}
        />
        <View style={styles.divider} />
        <ScenarioColumn
          label="IF LOSS"
          rating={stake.projected_rating_if_loss}
          rank={stake.projected_rank_if_loss}
          playoffProb={stake.playoff_prob_if_loss}
          color={colors.lossRed}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  header: { marginBottom: spacing.md },
  headerLabel: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: spacing.xs,
  },
  opponent: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700' },
  date: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
  currentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  currentLabel: { color: colors.silver, fontSize: fontSize.sm, flex: 1 },
  currentRating: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700', marginRight: spacing.sm },
  currentRank: { color: colors.silver, fontSize: fontSize.md, fontWeight: '600' },
  scenariosRow: { flexDirection: 'row' },
  scenario: { flex: 1, alignItems: 'center' },
  scenarioLabel: { fontSize: fontSize.xs, fontWeight: '800', letterSpacing: 1, marginBottom: spacing.sm },
  scenarioRating: { fontSize: fontSize.xl, fontWeight: '800', marginBottom: spacing.xs },
  scenarioDetail: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
  divider: { width: 1, backgroundColor: colors.border, marginHorizontal: spacing.sm },
});
