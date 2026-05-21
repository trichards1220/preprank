import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Modal, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import BadgeCard from '../components/BadgeCard';
import { mockBadges, mockUserBadges } from '../mock/data';

const RARITY_COLORS: Record<string, string> = {
  common: colors.silver,
  uncommon: colors.winGreen,
  rare: '#C22032',
  legendary: '#FFD700',
};

export default function BadgesScreen() {
  const [selectedBadge, setSelectedBadge] = useState<typeof mockBadges[0] | null>(null);
  const earnedIds = new Set(mockUserBadges.map(ub => ub.badge_id));
  const earnedCount = earnedIds.size;
  const totalCount = mockBadges.length;

  const isEarned = (badgeId: number) => earnedIds.has(badgeId);

  const getUserBadge = (badgeId: number) =>
    mockUserBadges.find(ub => ub.badge_id === badgeId);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Stats Header */}
      <View style={styles.statsCard}>
        <Ionicons name="ribbon" size={28} color={colors.crimson} />
        <Text style={styles.statsText}>
          {earnedCount} of {totalCount} badges earned
        </Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${(earnedCount / totalCount) * 100}%` as any }]} />
        </View>
      </View>

      {/* Badge Grid */}
      <View style={styles.grid}>
        {mockBadges.map(badge => {
          const earned = isEarned(badge.id);
          const userBadge = getUserBadge(badge.id);
          const color = RARITY_COLORS[badge.rarity] ?? colors.silver;

          return (
            <TouchableOpacity
              key={badge.id}
              style={[styles.gridItem, !earned && styles.gridItemLocked]}
              onPress={() => setSelectedBadge(badge)}
              activeOpacity={0.7}
            >
              <View style={[styles.gridIconCircle, { borderColor: earned ? color : colors.textMuted }]}>
                {earned ? (
                  <Ionicons name={badge.icon as any} size={28} color={color} />
                ) : (
                  <Ionicons name="lock-closed" size={22} color={colors.textMuted} />
                )}
              </View>
              <Text style={[styles.gridName, !earned && { color: colors.textMuted }]} numberOfLines={1}>
                {badge.name}
              </Text>
              <Text style={[styles.gridRarity, { color: earned ? color : colors.textMuted }]}>
                {badge.rarity.charAt(0).toUpperCase() + badge.rarity.slice(1)}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Detail Modal */}
      <Modal
        visible={selectedBadge !== null}
        transparent
        animationType="fade"
        onRequestClose={() => setSelectedBadge(null)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setSelectedBadge(null)}>
          <Pressable style={styles.modalCard} onPress={() => {}}>
            {selectedBadge && (
              <>
                <BadgeCard
                  badge={selectedBadge}
                  earned={isEarned(selectedBadge.id)}
                  earnedAt={getUserBadge(selectedBadge.id)?.earned_at}
                />
                <Text style={styles.modalCriteria}>
                  Criteria: {selectedBadge.criteria_type.replace(/_/g, ' ')}
                </Text>
                <TouchableOpacity
                  style={styles.modalClose}
                  onPress={() => setSelectedBadge(null)}
                >
                  <Text style={styles.modalCloseText}>Close</Text>
                </TouchableOpacity>
              </>
            )}
          </Pressable>
        </Pressable>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  statsCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statsText: {
    color: colors.white,
    fontSize: fontSize.lg,
    fontWeight: '700',
    marginTop: spacing.sm,
    marginBottom: spacing.sm,
  },
  progressBar: {
    width: '100%',
    height: 6,
    backgroundColor: colors.charcoal,
    borderRadius: 3,
  },
  progressFill: {
    height: 6,
    backgroundColor: colors.crimson,
    borderRadius: 3,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  gridItem: {
    width: '48%',
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  gridItemLocked: {
    opacity: 0.5,
  },
  gridIconCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: 2,
    backgroundColor: colors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  gridName: {
    color: colors.white,
    fontSize: fontSize.sm,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 2,
  },
  gridRarity: {
    fontSize: fontSize.xs,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  modalCard: {
    backgroundColor: colors.background,
    borderRadius: 16,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  modalCriteria: {
    color: colors.textMuted,
    fontSize: fontSize.sm,
    textAlign: 'center',
    marginTop: spacing.sm,
    textTransform: 'capitalize',
  },
  modalClose: {
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.sm,
    alignItems: 'center',
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  modalCloseText: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '600',
  },
});
