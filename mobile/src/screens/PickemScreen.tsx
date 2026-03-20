import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import {
  mockPickemContest, mockPickemSlates, mockPickemSlateGames,
  mockPickemSlateLabels, mockPickemPicks,
} from '../mock/data';

export default function PickemScreen({ navigation }: any) {
  const contest = mockPickemContest;
  const [picks, setPicks] = useState<Record<number, number>>(() => {
    const initial: Record<number, number> = {};
    mockPickemPicks.forEach(p => {
      initial[p.game_id] = p.picked_winner_team_id;
    });
    return initial;
  });

  const existingPicks = mockPickemPicks;
  const totalPicked = existingPicks.length;
  const correctPicks = existingPicks.filter(p => p.is_correct === true).length;
  const wrongPicks = existingPicks.filter(p => p.is_correct === false).length;
  const accuracy = totalPicked > 0 ? ((correctPicks / totalPicked) * 100).toFixed(1) : '0.0';
  const currentStreak = 4; // mock

  const handlePick = (gameId: number, teamId: number) => {
    setPicks(prev => ({ ...prev, [gameId]: teamId }));
  };

  const handleSubmit = () => {
    const pickCount = Object.keys(picks).length;
    Alert.alert('Picks Submitted', `You submitted ${pickCount} picks for ${contest.name}.`);
  };

  const getPickStatus = (gameId: number): 'correct' | 'wrong' | 'pending' | null => {
    const pick = existingPicks.find(p => p.game_id === gameId);
    if (!pick) return null;
    if (pick.is_correct === true) return 'correct';
    if (pick.is_correct === false) return 'wrong';
    return 'pending';
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.contestName}>{contest.name}</Text>
        <Text style={styles.contestMeta}>Week {contest.week_number} · {contest.season_year}</Text>
      </View>

      {/* Game Slate */}
      {mockPickemSlates.map(slate => {
        const game = mockPickemSlateGames.find(g => g.id === slate.game_id);
        if (!game) return null;
        const labels = mockPickemSlateLabels[game.id];
        if (!labels) return null;

        const selectedTeam = picks[game.id];
        const status = getPickStatus(game.id);

        return (
          <View key={slate.id} style={styles.gameCard}>
            <View style={styles.gameHeader}>
              {game.is_district && <Text style={styles.districtTag}>District</Text>}
              {status === 'correct' && (
                <Ionicons name="checkmark-circle" size={18} color={colors.winGreen} />
              )}
              {status === 'wrong' && (
                <Ionicons name="close-circle" size={18} color={colors.lossRed} />
              )}
              {status === 'pending' && (
                <Ionicons name="time" size={18} color={colors.silver} />
              )}
            </View>
            <View style={styles.teamsRow}>
              <TouchableOpacity
                style={[
                  styles.teamButton,
                  selectedTeam === game.home_team_id && styles.teamButtonSelected,
                ]}
                onPress={() => handlePick(game.id, game.home_team_id)}
                activeOpacity={0.7}
              >
                <Text style={[
                  styles.teamButtonText,
                  selectedTeam === game.home_team_id && styles.teamButtonTextSelected,
                ]}>
                  {labels.home}
                </Text>
              </TouchableOpacity>

              <Text style={styles.vsText}>vs</Text>

              <TouchableOpacity
                style={[
                  styles.teamButton,
                  selectedTeam === game.away_team_id && styles.teamButtonSelected,
                ]}
                onPress={() => handlePick(game.id, game.away_team_id)}
                activeOpacity={0.7}
              >
                <Text style={[
                  styles.teamButtonText,
                  selectedTeam === game.away_team_id && styles.teamButtonTextSelected,
                ]}>
                  {labels.away}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        );
      })}

      {/* Submit */}
      <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} activeOpacity={0.8}>
        <Text style={styles.submitText}>Submit Picks</Text>
      </TouchableOpacity>

      {/* My Accuracy */}
      <Text style={styles.sectionTitle}>MY ACCURACY</Text>
      <View style={styles.statsCard}>
        <View style={styles.statRow}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{correctPicks}/{totalPicked}</Text>
            <Text style={styles.statLabel}>Correct</Text>
          </View>
          <View style={styles.stat}>
            <Text style={[styles.statValue, { color: colors.winGreen }]}>{accuracy}%</Text>
            <Text style={styles.statLabel}>Accuracy</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{currentStreak}</Text>
            <Text style={styles.statLabel}>Streak</Text>
          </View>
        </View>
      </View>

      {/* Leaderboard Link */}
      <TouchableOpacity
        style={styles.leaderboardLink}
        onPress={() => navigation.navigate('PickemLeaderboard')}
        activeOpacity={0.7}
      >
        <Ionicons name="trophy-outline" size={20} color={colors.crimson} />
        <Text style={styles.leaderboardLinkText}>View Leaderboard</Text>
        <Ionicons name="chevron-forward" size={16} color={colors.textMuted} />
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  header: { marginBottom: spacing.lg },
  contestName: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  contestMeta: { color: colors.silver, fontSize: fontSize.sm, marginTop: 4 },
  gameCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  gameHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
    minHeight: 20,
  },
  districtTag: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '700',
    letterSpacing: 1,
  },
  teamsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teamButton: {
    flex: 1,
    backgroundColor: colors.cardElevated,
    borderRadius: 10,
    paddingVertical: spacing.sm + 2,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  teamButtonSelected: {
    backgroundColor: colors.crimson,
    borderColor: colors.crimson,
  },
  teamButtonText: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '700',
  },
  teamButtonTextSelected: {
    color: colors.white,
  },
  vsText: {
    color: colors.textMuted,
    fontSize: fontSize.sm,
    fontWeight: '600',
    marginHorizontal: spacing.sm,
  },
  submitButton: {
    backgroundColor: colors.crimson,
    borderRadius: 12,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  submitText: {
    color: colors.white,
    fontSize: fontSize.lg,
    fontWeight: '800',
  },
  sectionTitle: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginBottom: spacing.md,
  },
  statsCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.md,
  },
  statRow: {
    flexDirection: 'row',
  },
  stat: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    color: colors.white,
    fontSize: fontSize.xl,
    fontWeight: '800',
  },
  statLabel: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    marginTop: 2,
  },
  leaderboardLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  leaderboardLinkText: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '600',
    flex: 1,
  },
});
