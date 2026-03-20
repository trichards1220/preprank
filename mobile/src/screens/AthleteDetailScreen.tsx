import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';

export default function AthleteDetailScreen({ route }: any) {
  // Placeholder — athlete data model exists but stats are user-contributed
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={48} color={colors.textMuted} />
        </View>
        <Text style={styles.name}>Player Name</Text>
        <Text style={styles.meta}>QB · #12 · Class of 2026</Text>
        <Text style={styles.school}>Ruston Bearcats</Text>
      </View>

      <Text style={styles.sectionTitle}>TEAM</Text>
      <View style={styles.card}>
        <Text style={styles.teamName}>Ruston Football</Text>
        <Text style={styles.teamMeta}>Division I Non-Select · 2025</Text>
      </View>

      <Text style={styles.sectionTitle}>STATS</Text>
      <View style={styles.card}>
        <View style={styles.emptyStats}>
          <Ionicons name="stats-chart-outline" size={32} color={colors.textMuted} />
          <Text style={styles.emptyTitle}>No Stats Yet</Text>
          <Text style={styles.emptyText}>
            Player stats are contributed by coaches and users. Stats will appear here when available.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  profileCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.xl,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.cardElevated,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  name: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  meta: { color: colors.silver, fontSize: fontSize.md, marginTop: spacing.xs },
  school: { color: colors.crimson, fontSize: fontSize.sm, fontWeight: '600', marginTop: spacing.xs },
  sectionTitle: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  card: { backgroundColor: colors.card, borderRadius: 12, padding: spacing.md },
  teamName: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  teamMeta: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
  emptyStats: { alignItems: 'center', paddingVertical: spacing.xl },
  emptyTitle: { color: colors.white, fontSize: fontSize.md, fontWeight: '600', marginTop: spacing.sm },
  emptyText: { color: colors.textMuted, fontSize: fontSize.sm, textAlign: 'center', marginTop: spacing.xs, lineHeight: 20 },
});
