// mobile/app/_layout.tsx
// Root layout for Expo Router.
// This wraps every screen with the Stack navigator.
// We'll expand navigation in Checkpoint 3.

import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{ title: "MyTeams" }}
      />
    </Stack>
  );
}
