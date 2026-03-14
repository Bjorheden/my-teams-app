// mobile/app/_layout.tsx
// Root layout – wraps the app in AuthProvider and handles auth redirects.
//
// LEARNING NOTE – auth redirect pattern in Expo Router
//
// We can't use useAuth() in the same component that renders AuthProvider,
// so we split into two components:
//   RootLayout      – renders <AuthProvider> and nothing else
//   RootLayoutNav   – inside the provider, reads auth state + handles redirects
//
// useSegments() gives us the current route path as an array.
// e.g. navigating to /login → segments = ['login']
// We use this to avoid redirecting when already on an auth screen.

import { useEffect } from "react";
import { ActivityIndicator, View } from "react-native";
import { Tabs, useRouter, useSegments } from "expo-router";

import { AuthProvider, useAuth } from "./context/AuthContext";

function RootLayoutNav() {
  const { token, isLoading } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    const onAuthScreen =
      segments[0] === "login" || segments[0] === "register";

    if (!token && !onAuthScreen) {
      // Not logged in and not already on an auth screen → go to login
      router.replace("/login");
    } else if (token && onAuthScreen) {
      // Logged in but still on an auth screen → go to dashboard
      router.replace("/");
    }
  }, [token, isLoading, segments, router]);

  // Show a blank loading screen while restoring the token from SecureStore
  if (isLoading) {
    return (
      <View style={{ flex: 1, backgroundColor: "#0f172a", justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color="#3b82f6" size="large" />
      </View>
    );
  }

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
      {/* Auth screens exist as routes but are hidden from the tab bar */}
      <Tabs.Screen name="login" options={{ href: null }} />
      <Tabs.Screen name="register" options={{ href: null }} />
    </Tabs>
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <RootLayoutNav />
    </AuthProvider>
  );
}


