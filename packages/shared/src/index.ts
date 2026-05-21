// PrepRank shared types, constants, and validation schemas

export const BRAND = {
  colors: {
    crimson: '#C22032',
    charcoal: '#1A1A1E',
    steelGray: '#6B7280',
    silver: '#C0C0C0',
    white: '#FFFFFF',
  },
  fonts: {
    display: 'Barlow Condensed',
    body: 'Source Sans 3',
  },
} as const;

export const CLASSIFICATIONS = ['5A', '4A', '3A', '2A', '1A'] as const;
export type Classification = (typeof CLASSIFICATIONS)[number];

export const DIVISIONS = ['I', 'II', 'III', 'IV', 'V'] as const;
export type Division = (typeof DIVISIONS)[number];

export const DIVISION_TO_CLASSIFICATION: Record<Division, Classification> = {
  I: '5A',
  II: '4A',
  III: '3A',
  IV: '2A',
  V: '1A',
};

export const SUBSCRIPTION_TIERS = ['free', 'premium_monthly', 'season_pass', 'annual'] as const;
export type SubscriptionTier = (typeof SUBSCRIPTION_TIERS)[number];

export const GAME_STATUSES = ['scheduled', 'final', 'disputed', 'cancelled', 'forfeit'] as const;
export type GameStatus = (typeof GAME_STATUSES)[number];

export const SEASONS = ['fall', 'winter', 'spring'] as const;
export type Season = (typeof SEASONS)[number];
