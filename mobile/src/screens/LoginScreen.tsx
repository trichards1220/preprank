import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { colors, fontSize, spacing } from '../theme/colors';
import Wordmark from '../components/Wordmark';

export default function LoginScreen({ navigation }: any) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const handleSubmit = () => {
    // Mock: skip auth and go to main app
    navigation.replace('Main');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.inner}>
        <View style={styles.logoArea}>
          <Wordmark size="lg" />
          <Text style={styles.tagline}>Louisiana High School Sports{'\n'}Power Rankings & Predictions</Text>
        </View>

        <View style={styles.form}>
          {isRegister && (
            <View style={styles.nameRow}>
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="First name"
                placeholderTextColor={colors.textMuted}
                value={firstName}
                onChangeText={setFirstName}
              />
              <TextInput
                style={[styles.input, styles.halfInput]}
                placeholder="Last name"
                placeholderTextColor={colors.textMuted}
                value={lastName}
                onChangeText={setLastName}
              />
            </View>
          )}
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor={colors.textMuted}
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor={colors.textMuted}
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
          <TouchableOpacity style={styles.button} onPress={handleSubmit}>
            <Text style={styles.buttonText}>
              {isRegister ? 'Create Account' : 'Sign In'}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setIsRegister(!isRegister)}>
            <Text style={styles.toggleText}>
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  inner: { flex: 1, justifyContent: 'center', paddingHorizontal: spacing.xl },
  logoArea: { alignItems: 'center', marginBottom: spacing.xxl },
  tagline: { color: colors.silver, fontSize: fontSize.sm, textAlign: 'center', marginTop: spacing.md, lineHeight: 20 },
  form: {},
  nameRow: { flexDirection: 'row', gap: spacing.sm },
  halfInput: { flex: 1 },
  input: {
    backgroundColor: colors.inputBg,
    borderRadius: 10,
    padding: spacing.md,
    color: colors.white,
    fontSize: fontSize.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  button: {
    backgroundColor: colors.crimson,
    borderRadius: 10,
    padding: spacing.md,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  buttonText: { color: colors.white, fontSize: fontSize.md, fontWeight: '700' },
  toggleText: { color: colors.silver, fontSize: fontSize.sm, textAlign: 'center', marginTop: spacing.lg },
});
