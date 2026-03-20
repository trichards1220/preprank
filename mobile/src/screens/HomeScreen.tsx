import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import Wordmark from '../components/Wordmark';
import TeamRow from '../components/TeamRow';
import WhatsAtStakeCard from '../components/WhatsAtStakeCard';
import {
  mockFavorites, mockTeams, mockSchools, mockPowerRatings,
  mockProjections, mockWhatsAtStake, schoolNameForTeam,
} from '../mock/data';

type Tab = 'teams' | 'athletes';

export default function HomeScreen({ navigation }: any) {
  const [tab, setTab] = useState<Tab>('teams');

  const favoriteTeams = mockFavorites
    .filter(f => f.entity_type === 'team')
    .map(f => {
      const team = mockTeams.find(t => t.id === f.entity_id);
      const school = team ? mockSchools.find(s => s.id === team.school_id) : null;
      const pr = mockPowerRatings.find(p => p.team_id === f.entity_id);
      const proj = mockProjections[f.entity_id];
      return { favorite: f, team, school, pr, proj };
    })
    .filter(x => x.team && x.school);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Wordmark size="sm" />
      </View>

      <View style={styles.tabs}>
        <TouchableOpacity
          style={[styles.tab, tab === 'teams' && styles.tabActive]}
          onPress={() => setTab('teams')}
        >
          <Text style={[styles.tabText, tab === 'teams' && styles.tabTextActive]}>My Teams</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, tab === 'athletes' && styles.tabActive]}
          onPress={() => setTab('athletes')}
        >
          <Text style={[styles.tabText, tab === 'athletes' && styles.tabTextActive]}>My Athletes</Text>
        </TouchableOpacity>
      </View>

      {tab === 'teams' ? (
        <>
          {favoriteTeams.map(({ team, school, pr, proj }) => (
            <View key={team!.id} style={styles.teamCard}>
              <TeamRow
                schoolName={school!.name}
                division={team!.division}
                selectStatus={team!.select_status}
                powerRating={pr?.power_rating}
                rank={pr?.rank_in_division}
                record={pr ? `${8}-${2}` : undefined}
                onPress={() => navigation.navigate('TeamDetail', { teamId: team!.id })}
              />
              {proj && (
                <View style={styles.projRow}>
                  <View style={styles.projItem}>
                    <Text style={styles.projLabel}>Projected</Text>
                    <Text style={styles.projValue}>{proj.projected_rating_mean?.toFixed(2)}</Text>
                  </View>
                  <View style={styles.projItem}>
                    <Text style={styles.projLabel}>Playoffs</Text>
                    <Text style={[styles.projValue, { color: colors.winGreen }]}>
                      {proj.playoff_probability}%
                    </Text>
                  </View>
                  <View style={styles.projItem}>
                    <Text style={styles.projLabel}>Title</Text>
                    <Text style={styles.projValue}>{proj.championship_probability}%</Text>
                  </View>
                </View>
              )}
            </View>
          ))}

          <Text style={styles.sectionTitle}>WHAT'S AT STAKE</Text>
          <WhatsAtStakeCard stake={mockWhatsAtStake} />
        </>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyTitle}>Follow Athletes</Text>
          <Text style={styles.emptyText}>
            Follow your kid's team, star players, or recruits to get personalized updates on their stats and games.
          </Text>
          <TouchableOpacity style={styles.browseButton} onPress={() => navigation.navigate('Browse')}>
            <Text style={styles.browseButtonText}>Browse Teams</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  header: { paddingVertical: spacing.md, alignItems: 'center' },
  tabs: { flexDirection: 'row', marginBottom: spacing.lg, backgroundColor: colors.card, borderRadius: 10, padding: 3 },
  tab: { flex: 1, paddingVertical: spacing.sm, alignItems: 'center', borderRadius: 8 },
  tabActive: { backgroundColor: colors.crimson },
  tabText: { color: colors.silver, fontSize: fontSize.sm, fontWeight: '600' },
  tabTextActive: { color: colors.white },
  teamCard: { marginBottom: spacing.md },
  projRow: {
    flexDirection: 'row',
    backgroundColor: colors.cardElevated,
    borderRadius: 8,
    padding: spacing.sm,
    marginTop: -spacing.xs,
    marginHorizontal: spacing.xs,
  },
  projItem: { flex: 1, alignItems: 'center' },
  projLabel: { color: colors.textMuted, fontSize: fontSize.xs, marginBottom: 2 },
  projValue: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  sectionTitle: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  emptyState: { alignItems: 'center', paddingVertical: spacing.xxl },
  emptyTitle: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700', marginBottom: spacing.sm },
  emptyText: { color: colors.silver, fontSize: fontSize.sm, textAlign: 'center', lineHeight: 20, marginBottom: spacing.lg },
  browseButton: { backgroundColor: colors.crimson, borderRadius: 10, paddingHorizontal: spacing.xl, paddingVertical: spacing.sm },
  browseButtonText: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
});
