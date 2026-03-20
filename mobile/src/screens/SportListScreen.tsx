import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import { mockSports } from '../mock/data';

const seasonIcons: Record<string, string> = {
  fall: 'leaf-outline',
  winter: 'snow-outline',
  spring: 'flower-outline',
};

const seasonLabels: Record<string, string> = {
  fall: 'FALL',
  winter: 'WINTER',
  spring: 'SPRING',
};

export default function SportListScreen({ navigation }: any) {
  const grouped = mockSports.reduce<Record<string, typeof mockSports>>((acc, sport) => {
    (acc[sport.season] ??= []).push(sport);
    return acc;
  }, {});

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {['fall', 'winter', 'spring'].map(season => (
        <View key={season}>
          <View style={styles.seasonHeader}>
            <Ionicons
              name={seasonIcons[season] as any}
              size={16}
              color={colors.crimson}
            />
            <Text style={styles.seasonLabel}>{seasonLabels[season]}</Text>
          </View>
          {grouped[season]?.map(sport => (
            <TouchableOpacity
              key={sport.id}
              style={styles.sportRow}
              onPress={() => navigation.navigate('DivisionBrowser', { sportId: sport.id, sportName: sport.name })}
            >
              <Text style={styles.sportName}>{sport.name}</Text>
              {sport.has_power_rating && (
                <View style={styles.prBadge}>
                  <Text style={styles.prBadgeText}>PR</Text>
                </View>
              )}
              <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
            </TouchableOpacity>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  seasonHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  seasonLabel: { color: colors.crimson, fontSize: fontSize.xs, fontWeight: '800', letterSpacing: 2 },
  sportRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  sportName: { color: colors.white, fontSize: fontSize.md, fontWeight: '600', flex: 1 },
  prBadge: {
    backgroundColor: colors.crimson + '30',
    borderRadius: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    marginRight: spacing.sm,
  },
  prBadgeText: { color: colors.crimson, fontSize: fontSize.xs, fontWeight: '700' },
});
