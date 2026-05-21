import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import TeamRow from '../components/TeamRow';
import { mockStandings } from '../mock/data';

const DIVISIONS = ['I', 'II', 'III', 'IV'];
const SELECT_OPTIONS = ['Non-Select', 'Select'];

export default function DivisionBrowserScreen({ route, navigation }: any) {
  const { sportName } = route.params;
  const [division, setDivision] = useState('I');
  const [selectStatus, setSelectStatus] = useState('Non-Select');

  const bracket = mockStandings.find(
    s => s.division === division && s.select_status === selectStatus
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{sportName}</Text>

      <Text style={styles.filterLabel}>DIVISION</Text>
      <View style={styles.filterRow}>
        {DIVISIONS.map(d => (
          <TouchableOpacity
            key={d}
            style={[styles.chip, division === d && styles.chipActive]}
            onPress={() => setDivision(d)}
          >
            <Text style={[styles.chipText, division === d && styles.chipTextActive]}>{d}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.filterLabel}>TYPE</Text>
      <View style={styles.filterRow}>
        {SELECT_OPTIONS.map(s => (
          <TouchableOpacity
            key={s}
            style={[styles.chip, styles.chipWide, selectStatus === s && styles.chipActive]}
            onPress={() => setSelectStatus(s)}
          >
            <Text style={[styles.chipText, selectStatus === s && styles.chipTextActive]}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.bracketTitle}>
        Division {division} {selectStatus}
      </Text>
      <Text style={styles.bracketSub}>
        {bracket ? `Week ${bracket.week_number} · ${bracket.standings.length} teams` : 'No data'}
      </Text>

      {bracket?.standings.map((entry, i) => (
        <TeamRow
          key={entry.team_id}
          schoolName={`${i + 1}. ${entry.school_name}`}
          powerRating={entry.power_rating}
          rank={entry.rank_in_division}
          record={entry.wins != null ? `${entry.wins}-${entry.losses}` : undefined}
          onPress={() => navigation.navigate('TeamDetail', { teamId: entry.team_id })}
        />
      ))}

      {!bracket && (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No standings data for this bracket yet.</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  title: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800', marginBottom: spacing.lg },
  filterLabel: { color: colors.crimson, fontSize: fontSize.xs, fontWeight: '800', letterSpacing: 2, marginBottom: spacing.sm, marginTop: spacing.md },
  filterRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.sm },
  chip: {
    backgroundColor: colors.card,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  chipWide: { flex: 1, alignItems: 'center' },
  chipActive: { backgroundColor: colors.crimson, borderColor: colors.crimson },
  chipText: { color: colors.silver, fontSize: fontSize.sm, fontWeight: '600' },
  chipTextActive: { color: colors.white },
  bracketTitle: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700', marginTop: spacing.lg },
  bracketSub: { color: colors.silver, fontSize: fontSize.sm, marginBottom: spacing.md },
  empty: { alignItems: 'center', paddingVertical: spacing.xxl },
  emptyText: { color: colors.textMuted, fontSize: fontSize.md },
});
