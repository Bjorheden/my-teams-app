// mobile/app/index.tsx
// Checkpoint 1 – Placeholder home screen.
// This will become the Dashboard in Checkpoint 3.

import { StyleSheet, Text, View } from "react-native";
import { StatusBar } from "expo-status-bar";

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>⚽ MyTeams</Text>
      <Text style={styles.subtitle}>Your personalized football hub</Text>
      <Text style={styles.note}>
        Backend connects in Checkpoint 3.{"\n"}
        Start the API with: make up
      </Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 36,
    fontWeight: "700",
    color: "#f8fafc",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: "#94a3b8",
    marginBottom: 32,
  },
  note: {
    fontSize: 13,
    color: "#475569",
    textAlign: "center",
    lineHeight: 20,
  },
});
