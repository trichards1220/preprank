import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import { mockPickemLeaderboard, mockSchoolLeaderboard } from '../mock/data';

type Tab = 'players' | 'schools';

function TrophyIcon({ rank }: { rank: number }) {
  if (rank > 3) return null;
  const iconColors: Record<number, string> = { 1: '#FFD700', 2: colors.silver, 3: '#CD7F32' };
  return <Ionicons name="trophy" size={20} color={iconColors[rank]} />;
}

export default function PickemLeaderboardScreen() {
  const [tab, setTab] = useState<Tab>('players');

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Tabs */}
      <View style={styles.tabs}>
        <TouchableOpacity
          style={[styles.tab, tab === 'players' && styles.tabActive]}
          onPress={() => setTab('players')}
        >
          <Text style={[styles.tabText, tab === 'players' && styles.tabTextActive]}>Players</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, tab === 'schools' && styles.tabActive]}
          onPress={() => setTab('schools')}
        >
          <Text style={[styles.tabText, tab === 'schools' && styles.tabTextActive]}>Schools</Text>
        </TouchableOpacity>
      </View>

      {tab === 'players' ? (
        <>
          {mockPickemLeaderboard.map((entry, index) => {
            const rank = entry.rank ?? index + 1;
            const isTop3 = rank <= 3;
            return (
              <View key={entry.user_id} style={[styles.row, isTop3 && styles.rowTop3]}>
                <View style={[styles.rankBadge, isTop3 && styles.rankBadgeTop3]}>
                  {isTop3 ? (
                    <TrophyIcon rank={rank} />
                  ) : (
                    <Text style={styles.rankText}>{rank}</Text>
                  )}
                </View>
                <View style={styles.rowInfo}>
                  <Text style={[styles.rowName, isTop3 && styles.rowNameTop3]}>
                    User #{entry.user_id}
                  </Text>
                  <Text style={styles.rowSchool}>{entry.school_name}</Text>
                </View>
                <View style={styles.rowStats}>
                  <Text style={[styles.rowPoints, isTop3 && styles.rowPointsTop3]}>
                    {entry.total_points} pts
                  </Text>
                  <Text style={styles.rowDetail}>
                    {entry.correct_picks} correct · {entry.streak} streak
                  </Text>
                </View>
              </View>
            );
          })}
        </>
      ) : (
        <>
          {mockSchoolLeaderboard.map((entry, index) => {
            const rank = index + 1;
            const isTop3 = rank <= 3;
            return (
              <View key={entry.school_id} style={[styles.row, isTop3 && styles.rowTop3]}>
                <View style={[styles.rankBadge, isTop3 && styles.rankBadgeTop3]}>
                  {isTop3 ? (
                    <TrophyIcon rank={rank} />
                  ) : (
                    <Text style={styles.rankText}>{rank}</Text>
                  )}
                </View>
                <View style={styles.rowInfo}>
                  <Text style={[styles.rowName, isTop3 && styles.rowNameTop3]}>
                    {entry.school_name}
                  </Text>
                  <Text style={styles.rowSchool}>
                    {entry.participant_count} participants
                  </Text>
                </View>
                <View style={styles.rowStats}>
                  <Text style={[styles.rowPoints, isTop3 && styles.rowPointsTop3]}>
                    {entry.total_points} pts
                  </Text>
                  <Text style={styles.rowDetail}>
                    {entry.avg_accuracy != null ? `${entry.avg_accuracy}% avg` : '—'}
                  </Text>
                </View>
              </View>
            );
          })}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  tabs: {
    flexDirection: 'row',
    marginBottom: spacing.lg,
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: 3,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    borderRadius: 8,
  },
  tabActive: { backgroundColor: colors.crimson },
  tabText: { color: colors.silver, fontSize: fontSize.sm, fontWeight: '600' },
  tabTextActive: { color: colors.white },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  rowTop3: {
    borderColor: colors.crimson + '60',
  },
  rankBadge: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: colors.cardElevated,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  rankBadgeTop3: {
    backgroundColor: colors.charcoal,
  },
  rankText: {
    color: colors.silver,
    fontSize: fontSize.sm,
    fontWeight: '700',
  },
  rowInfo: { flex: 1 },
  rowName: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '600',
  },
  rowNameTop3: {
    fontWeight: '800',
    fontSize: fontSize.lg,
  },
  rowSchool: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    marginTop: 2,
  },
  rowStats: { alignItems: 'flex-end' },
  rowPoints: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '700',
  },
  rowPointsTop3: {
    color: colors.crimson,
    fontSize: fontSize.lg,
    fontWeight: '800',
  },
  rowDetail: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    marginTop: 2,
  },
});
