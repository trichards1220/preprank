import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';

import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import SportListScreen from '../screens/SportListScreen';
import DivisionBrowserScreen from '../screens/DivisionBrowserScreen';
import TeamDetailScreen from '../screens/TeamDetailScreen';
import SchoolDetailScreen from '../screens/SchoolDetailScreen';
import AthleteDetailScreen from '../screens/AthleteDetailScreen';
import StandingsScreen from '../screens/StandingsScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import SettingsScreen from '../screens/SettingsScreen';
import PickemScreen from '../screens/PickemScreen';
import PickemLeaderboardScreen from '../screens/PickemLeaderboardScreen';
import BadgesScreen from '../screens/BadgesScreen';
import SubscriptionScreen from '../screens/SubscriptionScreen';

const PrepRankTheme = {
  ...DefaultTheme,
  dark: true,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.crimson,
    background: colors.background,
    card: colors.steel,
    text: colors.white,
    border: colors.border,
    notification: colors.crimson,
  },
};

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const screenOptions = {
  headerStyle: { backgroundColor: colors.charcoal },
  headerTintColor: colors.white,
  headerTitleStyle: { fontWeight: '700' as const },
  headerShadowVisible: false,
};

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="HomeMain" component={HomeScreen} options={{ headerShown: false }} />
      <Stack.Screen name="TeamDetail" component={TeamDetailScreen} options={{ title: 'Team' }} />
      <Stack.Screen name="SchoolDetail" component={SchoolDetailScreen} options={{ title: 'School' }} />
      <Stack.Screen name="AthleteDetail" component={AthleteDetailScreen} options={{ title: 'Athlete' }} />
      <Stack.Screen name="Standings" component={StandingsScreen} options={{ title: 'Standings' }} />
    </Stack.Navigator>
  );
}

function PlayStack() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="PickemMain" component={PickemScreen} options={{ title: "Pick'em" }} />
      <Stack.Screen name="PickemLeaderboard" component={PickemLeaderboardScreen} options={{ title: 'Leaderboard' }} />
      <Stack.Screen name="Badges" component={BadgesScreen} options={{ title: 'Badges' }} />
    </Stack.Navigator>
  );
}

function BrowseStack() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="SportList" component={SportListScreen} options={{ title: 'Sports' }} />
      <Stack.Screen name="DivisionBrowser" component={DivisionBrowserScreen} options={{ title: 'Divisions' }} />
      <Stack.Screen name="TeamDetail" component={TeamDetailScreen} options={{ title: 'Team' }} />
      <Stack.Screen name="SchoolDetail" component={SchoolDetailScreen} options={{ title: 'School' }} />
      <Stack.Screen name="Standings" component={StandingsScreen} options={{ title: 'Standings' }} />
      <Stack.Screen name="AthleteDetail" component={AthleteDetailScreen} options={{ title: 'Athlete' }} />
    </Stack.Navigator>
  );
}

function NotificationsStack() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="NotificationsList" component={NotificationsScreen} options={{ title: 'Notifications' }} />
      <Stack.Screen name="TeamDetail" component={TeamDetailScreen} options={{ title: 'Team' }} />
    </Stack.Navigator>
  );
}

function SettingsStackNav() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="SettingsMain" component={SettingsScreen} options={{ title: 'Settings' }} />
      <Stack.Screen name="Badges" component={BadgesScreen} options={{ title: 'Badges' }} />
      <Stack.Screen name="Subscription" component={SubscriptionScreen} options={{ title: 'Subscription' }} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.charcoal,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          paddingBottom: 4,
          height: 56,
        },
        tabBarActiveTintColor: colors.crimson,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        tabBarIcon: ({ color, size }) => {
          const icons: Record<string, string> = {
            Home: 'home',
            Play: 'game-controller',
            Browse: 'grid',
            Notifications: 'notifications',
            Settings: 'settings',
          };
          return <Ionicons name={(icons[route.name] ?? 'ellipse') as any} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeStack} />
      <Tab.Screen name="Play" component={PlayStack} />
      <Tab.Screen name="Browse" component={BrowseStack} />
      <Tab.Screen
        name="Notifications"
        component={NotificationsStack}
        options={{ tabBarBadge: 2 }}
      />
      <Tab.Screen name="Settings" component={SettingsStackNav} />
    </Tab.Navigator>
  );
}

export default function Navigation() {
  return (
    <NavigationContainer theme={PrepRankTheme}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Main" component={MainTabs} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
