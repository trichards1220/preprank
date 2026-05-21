import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import PowerRatingBadge from './PowerRatingBadge';

interface Props {
  schoolName: string;
  division?: string | null;
  selectStatus?: string | null;
  powerRating?: number;
  rank?: number | null;
  record?: string;
  subtitle?: string;
  onPress?: () => void;
}

export default function TeamRow({
  schoolName, division, selectStatus, powerRating,
  rank, record, subtitle, onPress,
}: Props) {
  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.info}>
        <Text style={styles.name} numberOfLines={1}>{schoolName}</Text>
        {subtitle ? (
          <Text style={styles.meta}>{subtitle}</Text>
        ) : (
          <Text style={styles.meta}>
            {[division && `Div ${division}`, selectStatus, record].filter(Boolean).join(' · ')}
          </Text>
        )}
      </View>
      {powerRating != null && (
        <PowerRatingBadge rating={powerRating} rank={rank} size="sm" />
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  info: { flex: 1, marginRight: spacing.sm },
  name: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  meta: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
});
