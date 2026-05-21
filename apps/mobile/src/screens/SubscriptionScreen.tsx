import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, fontSize, spacing } from '../theme/colors';
import Wordmark from '../components/Wordmark';
import { mockUser } from '../mock/data';

interface Plan {
  tier: string;
  name: string;
  price: string;
  interval: string | null;
  features: string[];
  popular?: boolean;
  savings?: string;
}

const PLANS: Plan[] = [
  {
    tier: 'free',
    name: 'Free',
    price: '$0',
    interval: null,
    features: [
      'Current scores & schedules',
      'Basic standings',
      'Current week power ratings',
      "Pick'em contests",
    ],
  },
  {
    tier: 'premium_monthly',
    name: 'Premium Monthly',
    price: '$5.99',
    interval: '/month',
    features: [
      'Predictive engine & projected ratings',
      '"What\'s at stake" game previews',
      'Playoff probability simulator',
      'Push notifications for ranking changes',
      'Historical trends & comparisons',
      'My Athletes tracking',
    ],
  },
  {
    tier: 'season_pass',
    name: 'Season Pass',
    price: '$24.99',
    interval: '/season',
    features: [
      'All Premium features',
      '4-5 months of access',
      'Single sport season',
      'No auto-renewal',
    ],
    savings: 'Save 16% vs monthly',
  },
  {
    tier: 'annual',
    name: 'Annual',
    price: '$49.99',
    interval: '/year',
    features: [
      'All Premium features',
      'All sports, all year',
      'Less than $1/week',
    ],
    popular: true,
    savings: 'Save 30% vs monthly',
  },
];

function PlanCard({ plan, isCurrentPlan, onSelect }: {
  plan: Plan;
  isCurrentPlan: boolean;
  onSelect: () => void;
}) {
  const isFree = plan.tier === 'free';

  return (
    <View style={[
      styles.planCard,
      plan.popular && styles.planCardPopular,
      isCurrentPlan && styles.planCardCurrent,
    ]}>
      {plan.popular && (
        <View style={styles.popularBadge}>
          <Text style={styles.popularText}>BEST VALUE</Text>
        </View>
      )}

      <Text style={styles.planName}>{plan.name}</Text>
      <View style={styles.priceRow}>
        <Text style={styles.planPrice}>{plan.price}</Text>
        {plan.interval && <Text style={styles.planInterval}>{plan.interval}</Text>}
      </View>

      {plan.savings && (
        <View style={styles.savingsBadge}>
          <Text style={styles.savingsText}>{plan.savings}</Text>
        </View>
      )}

      <View style={styles.featureList}>
        {plan.features.map((feat, i) => (
          <View key={i} style={styles.featureRow}>
            <Ionicons
              name="checkmark-circle"
              size={16}
              color={isFree ? colors.silver : colors.winGreen}
            />
            <Text style={styles.featureText}>{feat}</Text>
          </View>
        ))}
      </View>

      {isCurrentPlan ? (
        <View style={styles.currentBadge}>
          <Ionicons name="checkmark-circle" size={16} color={colors.winGreen} />
          <Text style={styles.currentText}>Current Plan</Text>
        </View>
      ) : isFree ? null : (
        <TouchableOpacity
          style={[styles.selectButton, plan.popular && styles.selectButtonPopular]}
          onPress={onSelect}
        >
          <Text style={styles.selectButtonText}>
            {mockUser.subscription_tier === 'free' ? 'Subscribe' : 'Switch Plan'}
          </Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

export default function SubscriptionScreen({ navigation }: any) {
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const currentTier = mockUser.subscription_tier;
  const isActive = currentTier !== 'free';

  const handleSelectPlan = (tier: string) => {
    // In production: call POST /subscriptions/checkout with the tier
    // and open the returned Stripe Checkout URL in a WebView or browser
    Alert.alert(
      'Upgrade to ' + PLANS.find(p => p.tier === tier)?.name,
      'This would open Stripe Checkout or the App Store purchase flow.',
      [{ text: 'OK' }]
    );
  };

  const handleManage = () => {
    // In production: call POST /subscriptions/billing-portal
    // and open the returned URL
    Alert.alert(
      'Manage Subscription',
      'This would open the Stripe Billing Portal to manage your plan, update payment method, or cancel.',
      [{ text: 'OK' }]
    );
  };

  const handleRestore = () => {
    // In production: validate Apple/Google receipt
    Alert.alert(
      'Restore Purchases',
      'This would validate your App Store or Google Play receipt and restore your subscription.',
      [{ text: 'OK' }]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Wordmark size="sm" />
        <Text style={styles.headerTitle}>Choose Your Plan</Text>
        <Text style={styles.headerSub}>
          Unlock predictions, projections, and "what's at stake" analysis
        </Text>
      </View>

      {/* Current status */}
      {isActive && (
        <View style={styles.statusCard}>
          <View style={styles.statusRow}>
            <Ionicons name="star" size={20} color={colors.crimson} />
            <View style={styles.statusInfo}>
              <Text style={styles.statusTier}>
                {PLANS.find(p => p.tier === currentTier)?.name ?? currentTier}
              </Text>
              {mockUser.subscription_expires && (
                <Text style={styles.statusExpiry}>
                  Renews {new Date(mockUser.subscription_expires).toLocaleDateString('en-US', {
                    month: 'long', day: 'numeric', year: 'numeric',
                  })}
                </Text>
              )}
            </View>
          </View>
          <TouchableOpacity style={styles.manageButton} onPress={handleManage}>
            <Text style={styles.manageText}>Manage Subscription</Text>
            <Ionicons name="open-outline" size={14} color={colors.crimson} />
          </TouchableOpacity>
        </View>
      )}

      {/* Plan cards */}
      {PLANS.map(plan => (
        <PlanCard
          key={plan.tier}
          plan={plan}
          isCurrentPlan={plan.tier === currentTier}
          onSelect={() => handleSelectPlan(plan.tier)}
        />
      ))}

      {/* Restore purchases */}
      <TouchableOpacity style={styles.restoreButton} onPress={handleRestore}>
        <Text style={styles.restoreText}>Restore Purchases</Text>
      </TouchableOpacity>

      {/* Fine print */}
      <Text style={styles.finePrint}>
        Subscriptions are managed through Stripe, Apple App Store, or Google Play.
        Premium Monthly and Annual plans auto-renew unless cancelled at least 24 hours
        before the end of the current period. Season Pass is a one-time purchase with
        no auto-renewal. You can manage or cancel anytime from your account settings.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xxl },
  header: { alignItems: 'center', paddingVertical: spacing.xl },
  headerTitle: { color: colors.white, fontSize: fontSize.xl, fontWeight: '800', marginTop: spacing.md },
  headerSub: { color: colors.silver, fontSize: fontSize.sm, textAlign: 'center', marginTop: spacing.xs, lineHeight: 20 },
  statusCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.crimson + '40',
  },
  statusRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  statusInfo: { flex: 1 },
  statusTier: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  statusExpiry: { color: colors.silver, fontSize: fontSize.sm, marginTop: 2 },
  manageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    backgroundColor: colors.cardElevated,
    borderRadius: 8,
    padding: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  manageText: { color: colors.crimson, fontSize: fontSize.sm, fontWeight: '600' },
  planCard: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  planCardPopular: { borderColor: colors.crimson, borderWidth: 2 },
  planCardCurrent: { borderColor: colors.winGreen + '60' },
  popularBadge: {
    backgroundColor: colors.crimson,
    borderRadius: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    alignSelf: 'flex-start',
    marginBottom: spacing.sm,
  },
  popularText: { color: colors.white, fontSize: fontSize.xs, fontWeight: '800', letterSpacing: 1 },
  planName: { color: colors.white, fontSize: fontSize.lg, fontWeight: '700' },
  priceRow: { flexDirection: 'row', alignItems: 'baseline', marginTop: spacing.xs },
  planPrice: { color: colors.white, fontSize: fontSize.xxl, fontWeight: '800' },
  planInterval: { color: colors.silver, fontSize: fontSize.md, marginLeft: spacing.xs },
  savingsBadge: {
    backgroundColor: colors.winGreen + '20',
    borderRadius: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    alignSelf: 'flex-start',
    marginTop: spacing.sm,
  },
  savingsText: { color: colors.winGreen, fontSize: fontSize.xs, fontWeight: '700' },
  featureList: { marginTop: spacing.md },
  featureRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  featureText: { color: colors.silver, fontSize: fontSize.sm, flex: 1 },
  selectButton: {
    backgroundColor: colors.cardElevated,
    borderRadius: 10,
    padding: spacing.sm,
    alignItems: 'center',
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  selectButtonPopular: { backgroundColor: colors.crimson, borderColor: colors.crimson },
  selectButtonText: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  currentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    marginTop: spacing.md,
    paddingVertical: spacing.sm,
  },
  currentText: { color: colors.winGreen, fontSize: fontSize.sm, fontWeight: '600' },
  restoreButton: { alignItems: 'center', paddingVertical: spacing.md },
  restoreText: { color: colors.silver, fontSize: fontSize.sm, textDecorationLine: 'underline' },
  finePrint: {
    color: colors.textMuted,
    fontSize: fontSize.xs,
    textAlign: 'center',
    lineHeight: 16,
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.xl,
  },
});
