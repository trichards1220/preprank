import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import { mockNotifications } from '../mock/data';

const typeIcons: Record<string, string> = {
  ranking_change: 'trending-up',
  prediction_update: 'analytics',
  score_update: 'football',
  game_reminder: 'alarm',
};

const typeColors: Record<string, string> = {
  ranking_change: colors.winGreen,
  prediction_update: colors.crimson,
  score_update: colors.white,
  game_reminder: colors.silver,
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function NotificationsScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {mockNotifications.map(notif => (
        <TouchableOpacity
          key={notif.id}
          style={[styles.notifRow, !notif.read_status && styles.unread]}
          activeOpacity={0.7}
        >
          <View style={[styles.iconCircle, { backgroundColor: (typeColors[notif.notification_type] ?? colors.silver) + '20' }]}>
            <Ionicons
              name={(typeIcons[notif.notification_type] ?? 'notifications') as any}
              size={20}
              color={typeColors[notif.notification_type] ?? colors.silver}
            />
          </View>
          <View style={styles.notifContent}>
            <Text style={styles.notifTitle}>{notif.title}</Text>
            <Text style={styles.notifMessage} numberOfLines={2}>{notif.message}</Text>
            <Text style={styles.notifTime}>{notif.sent_at ? timeAgo(notif.sent_at) : ''}</Text>
          </View>
          {!notif.read_status && <View style={styles.unreadDot} />}
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  notifRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  unread: { borderLeftWidth: 3, borderLeftColor: colors.crimson },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  notifContent: { flex: 1 },
  notifTitle: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  notifMessage: { color: colors.silver, fontSize: fontSize.sm, marginTop: 4, lineHeight: 19 },
  notifTime: { color: colors.textMuted, fontSize: fontSize.xs, marginTop: spacing.xs },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.crimson,
    marginTop: 6,
  },
});
