import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Switch, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import Wordmark from '../components/Wordmark';
import BadgeCard from '../components/BadgeCard';
import { mockUser, mockUserBadges } from '../mock/data';

function SettingsRow({ icon, label, value, onPress }: {
  icon: string; label: string; value?: string; onPress?: () => void;
}) {
  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.7}>
      <Ionicons name={icon as any} size={20} color={colors.silver} />
      <Text style={styles.rowLabel}>{label}</Text>
      {value && <Text style={styles.rowValue}>{value}</Text>}
      <Ionicons name="chevron-forward" size={16} color={colors.textMuted} />
    </TouchableOpacity>
  );
}

function ToggleRow({ icon, label, value, onToggle }: {
  icon: string; label: string; value: boolean; onToggle: (v: boolean) => void;
}) {
  return (
    <View style={styles.row}>
      <Ionicons name={icon as any} size={20} color={colors.silver} />
      <Text style={[styles.rowLabel, { flex: 1 }]}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: colors.cardElevated, true: colors.crimson + '80' }}
        thumbColor={value ? colors.crimson : colors.silver}
      />
    </View>
  );
}

export default function SettingsScreen({ navigation }: any) {
  const [scoreNotifs, setScoreNotifs] = useState(true);
  const [rankNotifs, setRankNotifs] = useState(true);
  const [predNotifs, setPredNotifs] = useState(true);
  const [reminderNotifs, setReminderNotifs] = useState(false);

  const tierDisplay: Record<string, string> = {
    free: 'Free',
    premium_monthly: 'Premium Monthly',
    season_pass: 'Season Pass',
    annual: 'Annual',
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Profile */}
      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {mockUser.first_name?.[0]}{mockUser.last_name?.[0]}
          </Text>
        </View>
        <Text style={styles.profileName}>
          {mockUser.first_name} {mockUser.last_name}
        </Text>
        <Text style={styles.profileEmail}>{mockUser.email}</Text>
      </View>

      {/* Subscription */}
      <Text style={styles.sectionTitle}>SUBSCRIPTION</Text>
      <View style={styles.subCard}>
        <View style={styles.subBadge}>
          <Ionicons name="star" size={16} color={colors.crimson} />
          <Text style={styles.subTier}>{tierDisplay[mockUser.subscription_tier] ?? 'Free'}</Text>
        </View>
        {mockUser.subscription_expires && (
          <Text style={styles.subExpiry}>
            Renews {new Date(mockUser.subscription_expires).toLocaleDateString('en-US', {
              month: 'long', day: 'numeric', year: 'numeric',
            })}
          </Text>
        )}
        <TouchableOpacity style={styles.manageButton} onPress={() => navigation.navigate('Subscription')}>
          <Text style={styles.manageButtonText}>Manage Subscription</Text>
        </TouchableOpacity>
      </View>

      {/* My Badges */}
      <View style={styles.badgeSectionHeader}>
        <Text style={styles.sectionTitle}>MY BADGES</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Badges')} activeOpacity={0.7}>
          <Text style={styles.viewAllText}>View All</Text>
        </TouchableOpacity>
      </View>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.badgeScroll}
        contentContainerStyle={styles.badgeScrollContent}
      >
        {mockUserBadges.map(badge => (
          <BadgeCard key={badge.id} badge={badge} compact />
        ))}
      </ScrollView>

      {/* Notifications */}
      <Text style={styles.sectionTitle}>NOTIFICATION PREFERENCES</Text>
      <View style={styles.section}>
        <ToggleRow icon="football-outline" label="Score updates" value={scoreNotifs} onToggle={setScoreNotifs} />
        <ToggleRow icon="trending-up-outline" label="Ranking changes" value={rankNotifs} onToggle={setRankNotifs} />
        <ToggleRow icon="analytics-outline" label="Prediction updates" value={predNotifs} onToggle={setPredNotifs} />
        <ToggleRow icon="alarm-outline" label="Game reminders" value={reminderNotifs} onToggle={setReminderNotifs} />
      </View>

      {/* Account */}
      <Text style={styles.sectionTitle}>ACCOUNT</Text>
      <View style={styles.section}>
        <SettingsRow icon="person-outline" label="Edit Profile" />
        <SettingsRow icon="lock-closed-outline" label="Change Password" />
        <SettingsRow icon="document-text-outline" label="Privacy Policy" />
        <SettingsRow icon="help-circle-outline" label="Support" />
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={() => navigation.replace('Login')}>
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Wordmark size="sm" />
        <Text style={styles.version}>v0.1.0</Text>
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
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.crimson,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  avatarText: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800' },
  profileName: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700' },
  profileEmail: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
  sectionTitle: {
    color: colors.crimson,
    fontSize: fontSize.xs,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  subCard: { backgroundColor: colors.card, borderRadius: 12, padding: spacing.md, marginBottom: spacing.sm },
  subBadge: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  subTier: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  subExpiry: { color: colors.silver, fontSize: fontSize.sm, marginBottom: spacing.md },
  manageButton: {
    backgroundColor: colors.cardElevated,
    borderRadius: 8,
    padding: spacing.sm,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  manageButtonText: { color: colors.white, fontSize: fontSize.sm, fontWeight: '600' },
  badgeSectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  viewAllText: {
    color: colors.crimson,
    fontSize: fontSize.sm,
    fontWeight: '700',
  },
  badgeScroll: {
    marginBottom: spacing.sm,
  },
  badgeScrollContent: {
    paddingVertical: spacing.xs,
  },
  section: {
    backgroundColor: colors.card,
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    gap: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  rowLabel: { color: colors.white, fontSize: fontSize.md },
  rowValue: { color: colors.silver, fontSize: fontSize.sm, marginLeft: 'auto', marginRight: spacing.sm },
  logoutButton: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: colors.lossRed + '40',
  },
  logoutText: { color: colors.lossRed, fontSize: fontSize.md, fontWeight: '600' },
  footer: { alignItems: 'center', marginTop: spacing.xl, paddingBottom: spacing.xl },
  version: { color: colors.textMuted, fontSize: fontSize.xs, marginTop: spacing.sm },
});
