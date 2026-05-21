import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import { mockStandings } from '../mock/data';

export default function StandingsScreen({ route, navigation }: any) {
  const { sportId, sportName, division, selectStatus } = route.params ?? {};

  const bracket = mockStandings.find(
    s => s.division === (division ?? 'I') && s.select_status === (selectStatus ?? 'Non-Select')
  );

  if (!bracket) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>No standings data available</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        Division {bracket.division} {bracket.select_status}
      </Text>
      <Text style={styles.subtitle}>
        {sportName ?? 'Football'} · {bracket.season_year} · Week {bracket.week_number}
      </Text>

      {/* Table header */}
      <View style={styles.tableHeader}>
        <Text style={[styles.headerCell, styles.rankCol]}>#</Text>
        <Text style={[styles.headerCell, styles.nameCol]}>School</Text>
        <Text style={[styles.headerCell, styles.recordCol]}>W-L</Text>
        <Text style={[styles.headerCell, styles.ratingCol]}>PR</Text>
        <Text style={[styles.headerCell, styles.sfCol]}>SF</Text>
      </View>

      {bracket.standings.map((entry, i) => {
        const isPlayoffLine = i === 7; // top 8 make playoffs (for 32-team bracket, top 32 but show cutoff at 8)
        return (
          <View key={entry.team_id}>
            {isPlayoffLine && <View style={styles.cutoffLine} />}
            <View
              style={[styles.tableRow, i % 2 === 0 && styles.tableRowAlt]}
            >
              <Text style={[styles.cell, styles.rankCol, styles.rankText]}>
                {i + 1}
              </Text>
              <Text
                style={[styles.cell, styles.nameCol, styles.nameText]}
                numberOfLines={1}
                onPress={() => navigation.navigate('TeamDetail', { teamId: entry.team_id })}
              >
                {entry.school_name}
              </Text>
              <Text style={[styles.cell, styles.recordCol]}>
                {entry.wins != null ? `${entry.wins}-${entry.losses}` : '—'}
              </Text>
              <Text style={[styles.cell, styles.ratingCol, styles.ratingText]}>
                {entry.power_rating.toFixed(2)}
              </Text>
              <Text style={[styles.cell, styles.sfCol]}>
                {entry.strength_factor?.toFixed(2) ?? '—'}
              </Text>
            </View>
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  emptyText: { color: colors.textMuted, fontSize: fontSize.md, textAlign: 'center', marginTop: spacing.xxl },
  title: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  subtitle: { color: colors.silver, fontSize: fontSize.sm, marginTop: spacing.xs, marginBottom: spacing.lg },
  tableHeader: {
    flexDirection: 'row',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerCell: { color: colors.textMuted, fontSize: fontSize.xs, fontWeight: '700' },
  tableRow: { flexDirection: 'row', paddingVertical: spacing.sm + 2 },
  tableRowAlt: { backgroundColor: colors.card + '40' },
  cell: { color: colors.silver, fontSize: fontSize.sm },
  rankCol: { width: 30 },
  rankText: { color: colors.crimson, fontWeight: '700' },
  nameCol: { flex: 1, paddingRight: spacing.sm },
  nameText: { color: colors.white, fontWeight: '600' },
  recordCol: { width: 45, textAlign: 'center' },
  ratingCol: { width: 55, textAlign: 'right' },
  ratingText: { color: colors.white, fontWeight: '700' },
  sfCol: { width: 50, textAlign: 'right' },
  cutoffLine: {
    height: 2,
    backgroundColor: colors.crimson,
    marginVertical: spacing.xs,
    opacity: 0.5,
  },
});
