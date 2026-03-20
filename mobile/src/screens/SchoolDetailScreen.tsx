import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import TeamRow from '../components/TeamRow';
import { mockSchools, mockTeams, mockSports, mockPowerRatings } from '../mock/data';

export default function SchoolDetailScreen({ route, navigation }: any) {
  const { schoolId } = route.params;
  const school = mockSchools.find(s => s.id === schoolId);
  const teams = mockTeams.filter(t => t.school_id === schoolId);

  if (!school) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>School not found</Text>
      </View>
    );
  }

  const teamsBySport = teams.reduce<Record<string, typeof teams>>((acc, team) => {
    const sport = mockSports.find(s => s.id === team.sport_id);
    const key = sport?.name ?? 'Unknown';
    (acc[key] ??= []).push(team);
    return acc;
  }, {});

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.name}>{school.name}</Text>

      <View style={styles.infoGrid}>
        {school.city && (
          <InfoItem icon="location-outline" label="City" value={school.city} />
        )}
        {school.parish && (
          <InfoItem icon="map-outline" label="Parish" value={school.parish} />
        )}
        {school.classification && (
          <InfoItem icon="layers-outline" label="Class" value={school.classification} />
        )}
        {school.division && (
          <InfoItem icon="grid-outline" label="Division" value={school.division} />
        )}
        {school.select_status && (
          <InfoItem icon="shield-outline" label="Status" value={school.select_status} />
        )}
        {school.enrollment && (
          <InfoItem icon="people-outline" label="Enrollment" value={school.enrollment.toString()} />
        )}
      </View>

      {Object.entries(teamsBySport).map(([sportName, sportTeams]) => (
        <View key={sportName}>
          <Text style={styles.sportLabel}>{sportName.toUpperCase()}</Text>
          {sportTeams.map(team => {
            const pr = mockPowerRatings.find(p => p.team_id === team.id);
            return (
              <TeamRow
                key={team.id}
                schoolName={`${team.season_year} Season`}
                subtitle={team.head_coach ? `Coach ${team.head_coach}` : undefined}
                division={team.division}
                selectStatus={team.select_status}
                powerRating={pr?.power_rating}
                rank={pr?.rank_in_division}
                onPress={() => navigation.navigate('TeamDetail', { teamId: team.id })}
              />
            );
          })}
        </View>
      ))}
    </ScrollView>
  );
}

function InfoItem({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <View style={styles.infoItem}>
      <Ionicons name={icon as any} size={16} color={colors.crimson} />
      <View>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  emptyText: { color: colors.textMuted, fontSize: fontSize.md, textAlign: 'center', marginTop: spacing.xxl },
  name: { color: colors.white, fontSize: fontSize.xxl, fontWeight: '800', marginBottom: spacing.lg },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  infoItem: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, width: '45%' },
  infoLabel: { color: colors.textMuted, fontSize: fontSize.xs },
  infoValue: { color: colors.white, fontSize: fontSize.sm, fontWeight: '600' },
  sportLabel: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
});
