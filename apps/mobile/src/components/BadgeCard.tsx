import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Share } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import type { UserBadge, BadgeInfo } from '../types/api';

const RARITY_COLORS: Record<string, string> = {
  common: colors.silver,
  uncommon: colors.winGreen,
  rare: '#C22032',
  legendary: '#FFD700',
};

function rarityColor(rarity: string): string {
  return RARITY_COLORS[rarity] ?? colors.silver;
}

interface Props {
  badge: UserBadge | BadgeInfo;
  earned?: boolean;
  compact?: boolean;
  earnedAt?: string | null;
}

export default function BadgeCard({ badge, earned = true, compact = false, earnedAt }: Props) {
  const isUserBadge = 'badge_name' in badge;
  const name = isUserBadge ? badge.badge_name : badge.name;
  const icon = isUserBadge ? badge.badge_icon : badge.icon;
  const rarity = isUserBadge ? badge.badge_rarity : badge.rarity;
  const description = isUserBadge ? badge.description : badge.description;
  const dateStr = isUserBadge ? badge.earned_at : earnedAt;
  const color = rarityColor(rarity);

  const handleShare = async () => {
    await Share.share({
      message: `\uD83C\uDFC6 I earned the ${name} badge on PrepRank!`,
    });
  };

  if (compact) {
    return (
      <View style={[compactStyles.card, !earned && compactStyles.cardLocked]}>
        <View style={[compactStyles.iconCircle, { borderColor: earned ? color : colors.textMuted }]}>
          {earned ? (
            <Ionicons name={icon as any} size={20} color={color} />
          ) : (
            <Ionicons name="lock-closed" size={16} color={colors.textMuted} />
          )}
        </View>
        <Text style={[compactStyles.name, !earned && { color: colors.textMuted }]} numberOfLines={1}>
          {name}
        </Text>
        <Text style={[compactStyles.rarity, { color: earned ? color : colors.textMuted }]}>
          {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.card, !earned && styles.cardLocked]}>
      <View style={styles.topRow}>
        <View style={[styles.iconCircle, { borderColor: earned ? color : colors.textMuted }]}>
          {earned ? (
            <Ionicons name={icon as any} size={24} color={color} />
          ) : (
            <Ionicons name="lock-closed" size={20} color={colors.textMuted} />
          )}
        </View>
        <View style={styles.info}>
          <Text style={[styles.name, !earned && { color: colors.textMuted }]}>{name}</Text>
          <Text style={[styles.rarity, { color: earned ? color : colors.textMuted }]}>
            {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
          </Text>
        </View>
        {earned && (
          <TouchableOpacity style={styles.shareButton} onPress={handleShare} activeOpacity={0.7}>
            <Ionicons name="share-outline" size={16} color={colors.white} />
          </TouchableOpacity>
        )}
      </View>

      {description && (
        <Text style={[styles.description, !earned && { color: colors.textMuted }]}>
          {description}
        </Text>
      )}

      {earned && dateStr && (
        <Text style={styles.earnedDate}>
          Earned {new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
          })}
        </Text>
      )}
    </View>
  );
}

const compactStyles = StyleSheet.create({
  card: {
    width: 90,
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: spacing.sm,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardLocked: {
    opacity: 0.5,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 2,
    backgroundColor: colors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xs,
  },
  name: {
    color: colors.white,
    fontSize: fontSize.xs,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 2,
  },
  rarity: {
    fontSize: 9,
    fontWeight: '600',
    textAlign: 'center',
  },
});

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.sm,
  },
  cardLocked: {
    opacity: 0.6,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 2,
    backgroundColor: colors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  info: {
    flex: 1,
  },
  name: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: '700',
  },
  rarity: {
    fontSize: fontSize.xs,
    fontWeight: '600',
    marginTop: 2,
  },
  shareButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.cardElevated,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  description: {
    color: colors.silver,
    fontSize: fontSize.sm,
    marginTop: spacing.sm,
    lineHeight: 18,
  },
  earnedDate: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    marginTop: spacing.sm,
  },
});
