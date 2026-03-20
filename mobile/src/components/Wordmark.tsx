import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, fontSize } from '../theme/colors';

interface Props {
  size?: 'sm' | 'md' | 'lg';
}

const sizes = {
  sm: { font: fontSize.lg, slash: 20 },
  md: { font: fontSize.xxl, slash: 32 },
  lg: { font: fontSize.hero, slash: 40 },
};

export default function Wordmark({ size = 'md' }: Props) {
  const s = sizes[size];
  return (
    <View style={styles.row}>
      <Text style={[styles.prep, { fontSize: s.font }]}>PREP</Text>
      <View style={[styles.slash, { height: s.slash, width: s.slash * 0.18 }]} />
      <Text style={[styles.rank, { fontSize: s.font }]}>RANK</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center' },
  prep: { color: colors.white, fontWeight: '900', letterSpacing: 2 },
  slash: {
    backgroundColor: colors.crimson,
    marginHorizontal: 6,
    transform: [{ skewX: '-12deg' }],
    borderRadius: 2,
  },
  rank: { color: colors.crimson, fontWeight: '900', letterSpacing: 2 },
});
