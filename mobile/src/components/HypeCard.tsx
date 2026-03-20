import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Share } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import type { HypeScore } from '../types/api';
import { schoolNameForTeam } from '../mock/data';

interface Props {
  hype: HypeScore;
}

function getMomentumArrow(direction: string): { symbol: string; color: string } {
  switch (direction) {
    case 'rising': return { symbol: '\u2191', color: colors.winGreen };
    case 'falling': return { symbol: '\u2193', color: colors.lossRed };
    default: return { symbol: '\u2192', color: colors.silver };
  }
}

export default function HypeCard({ hype }: Props) {
  const schoolName = schoolNameForTeam(hype.team_id);
  const momentum = getMomentumArrow(hype.momentum_direction);
  const ratingChangePositive = hype.rating_change_4wk != null && hype.rating_change_4wk > 0;
  const ratingChangeNegative = hype.rating_change_4wk != null && hype.rating_change_4wk < 0;

  const handleShare = async () => {
    const streakText = hype.win_streak > 0 ? ` | ${hype.win_streak}-game win streak` : '';
    await Share.share({
      message: `\uD83D\uDD25 ${schoolName} Hype Score: ${hype.hype_score} ${momentum.symbol}${streakText} | PrepRank`,
    });
  };

  return (
    <View style={styles.card}>
      <View style={styles.gradient} />

      <View style={styles.headerRow}>
        <Text style={styles.label}>HYPE SCORE</Text>
        <TouchableOpacity style={styles.shareButton} onPress={handleShare} activeOpacity={0.7}>
          <Ionicons name="share-outline" size={18} color={colors.white} />
          <Text style={styles.shareText}>Share</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.scoreRow}>
        <Text style={styles.score}>{hype.hype_score.toFixed(1)}</Text>
        <Text style={[styles.arrow, { color: momentum.color }]}>{momentum.symbol}</Text>
        <Text style={[styles.directionLabel, { color: momentum.color }]}>
          {hype.momentum_direction.charAt(0).toUpperCase() + hype.momentum_direction.slice(1)}
        </Text>
      </View>

      <View style={styles.statsRow}>
        {hype.win_streak > 0 && (
          <View style={styles.streakBadge}>
            <Ionicons name="flame" size={14} color={colors.crimson} />
            <Text style={styles.streakText}>{hype.win_streak}W Streak</Text>
          </View>
        )}

        {hype.rating_change_4wk != null && (
          <View style={styles.changeBadge}>
            <Text style={styles.changeLabel}>4-Week</Text>
            <Text style={[
              styles.changeValue,
              ratingChangePositive && { color: colors.winGreen },
              ratingChangeNegative && { color: colors.lossRed },
            ]}>
              {ratingChangePositive ? '+' : ''}{hype.rating_change_4wk.toFixed(1)}
            </Text>
          </View>
        )}
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
    overflow: 'hidden',
  },
  gradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 80,
    backgroundColor: colors.steel,
    opacity: 0.5,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  label: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: colors.cardElevated,
    borderRadius: 8,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  shareText: {
    color: colors.white,
    fontSize: fontSize.xs,
    fontWeight: '600',
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: spacing.md,
  },
  score: {
    color: colors.white,
    fontSize: fontSize.hero,
    fontWeight: '900',
    marginRight: spacing.sm,
  },
  arrow: {
    fontSize: fontSize.xxl,
    fontWeight: '800',
    marginRight: spacing.xs,
  },
  directionLabel: {
    fontSize: fontSize.md,
    fontWeight: '700',
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: colors.charcoal,
    borderRadius: 8,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  streakText: {
    color: colors.white,
    fontSize: fontSize.sm,
    fontWeight: '700',
  },
  changeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: colors.charcoal,
    borderRadius: 8,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  changeLabel: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    fontWeight: '600',
  },
  changeValue: {
    color: colors.silver,
    fontSize: fontSize.sm,
    fontWeight: '700',
  },
});
