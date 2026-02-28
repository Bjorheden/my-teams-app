// mobile/app/_layout.tsx
// Root layout – switched from Stack to Tabs in Checkpoint 3.
//
// LEARNING NOTE – Expo Router layouts
// _layout.tsx wraps every sibling screen in this directory.
// Tabs gives us a bottom tab bar for free with no extra setup.
// The `name` prop matches the filename (index.tsx → "index", search.tsx → "search").

import { Tabs } from "expo-router";

export default function RootLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#3b82f6",
        tabBarInactiveTintColor: "#64748b",
        tabBarStyle: { backgroundColor: "#0f172a", borderTopColor: "#1e293b" },
        headerStyle: { backgroundColor: "#0f172a" },
        headerTintColor: "#f8fafc",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: "Dashboard", tabBarLabel: "Dashboard" }}
      />
      <Tabs.Screen
        name="search"
        options={{ title: "Find Teams", tabBarLabel: "Search" }}
      />
    </Tabs>
  );
}

