import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';

interface Props {
  rating: number;
  rank?: number | null;
  size?: 'sm' | 'md';
}

export default function PowerRatingBadge({ rating, rank, size = 'md' }: Props) {
  const isSmall = size === 'sm';
  return (
    <View style={[styles.container, isSmall && styles.containerSm]}>
      <Text style={[styles.rating, isSmall && styles.ratingSm]}>
        {rating.toFixed(2)}
      </Text>
      {rank != null && (
        <Text style={[styles.rank, isSmall && styles.rankSm]}>#{rank}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.crimson,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    minWidth: 80,
  },
  containerSm: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    minWidth: 60,
  },
  rating: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  ratingSm: { fontSize: fontSize.md },
  rank: { color: 'rgba(255,255,255,0.8)', fontSize: fontSize.sm, fontWeight: '600', marginTop: 2 },
  rankSm: { fontSize: fontSize.xs },
});
