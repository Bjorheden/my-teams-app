// mobile/app/index.tsx – Dashboard screen
// ─────────────────────────────────────────────────────────────────
// LEARNING NOTE – useEffect + fetch pattern
//
// React Native doesn't have a built-in data-fetching library.
// The basic pattern is:
//   1. useState to hold data, loading state, and errors
//   2. useEffect to trigger the fetch when the component mounts
//   3. Render based on those state values
//
// This is intentionally simple. In a real app you'd add a library
// like React Query or SWR for caching, refetching, and deduplication.
// ─────────────────────────────────────────────────────────────────

import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";

import { getDashboard, unfollowTeam } from "./api/client";
import type { DashboardOut, Fixture, StandingRow, Team } from "./types";

// ── Sub-components ───────────────────────────────────────────────

function FollowedTeamChip({
  team,
  onUnfollow,
}: {
  team: Team;
  onUnfollow: (id: string) => void;
}) {
  return (
    <View style={styles.chip}>
      <Text style={styles.chipEmoji}>{team.crest_emoji}</Text>
      <Text style={styles.chipName}>{team.short_name}</Text>
      <TouchableOpacity onPress={() => onUnfollow(team.id)}>
        <Text style={styles.chipRemove}>✕</Text>
      </TouchableOpacity>
    </View>
  );
}

function FixtureCard({ fixture }: { fixture: Fixture }) {
  const isFinished = fixture.status === "finished";
  return (
    <View style={styles.card}>
      <Text style={styles.cardMeta}>
        {fixture.competition} · {fixture.date}
      </Text>
      <View style={styles.fixtureRow}>
        <Text style={styles.teamName} numberOfLines={1}>
          {fixture.home_team_name}
        </Text>
        <Text style={styles.score}>
          {isFinished
            ? `${fixture.home_goals} – ${fixture.away_goals}`
            : "vs"}
        </Text>
        <Text style={[styles.teamName, styles.textRight]} numberOfLines={1}>
          {fixture.away_team_name}
        </Text>
      </View>
      <Text style={[styles.cardMeta, isFinished ? styles.finished : styles.scheduled]}>
        {isFinished ? "Full time" : "Upcoming"}
      </Text>
    </View>
  );
}

function StandingTable({ rows }: { rows: StandingRow[] }) {
  return (
    <View style={styles.table}>
      <View style={styles.tableHeader}>
        <Text style={[styles.tableCell, styles.tablePos]}>#</Text>
        <Text style={[styles.tableCell, styles.tableName]}>Team</Text>
        <Text style={styles.tableCell}>P</Text>
        <Text style={styles.tableCell}>W</Text>
        <Text style={styles.tableCell}>D</Text>
        <Text style={styles.tableCell}>L</Text>
        <Text style={[styles.tableCell, styles.tablePts]}>Pts</Text>
      </View>
      {rows.map((row) => (
        <View key={row.team_id} style={styles.tableRow}>
          <Text style={[styles.tableCell, styles.tablePos]}>{row.position}</Text>
          <Text style={[styles.tableCell, styles.tableName]} numberOfLines={1}>
            {row.team_name}
          </Text>
          <Text style={styles.tableCell}>{row.played}</Text>
          <Text style={styles.tableCell}>{row.won}</Text>
          <Text style={styles.tableCell}>{row.drawn}</Text>
          <Text style={styles.tableCell}>{row.lost}</Text>
          <Text style={[styles.tableCell, styles.tablePts]}>{row.points}</Text>
        </View>
      ))}
    </View>
  );
}

// ── Main screen ──────────────────────────────────────────────────

export default function DashboardScreen() {
  const [data, setData] = useState<DashboardOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const result = await getDashboard();
      setData(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleUnfollow = async (teamId: string) => {
    try {
      await unfollowTeam(teamId);
      await load(); // refresh dashboard after unfollow
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to unfollow");
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    load();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading dashboard…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>⚠️ {error}</Text>
        <Text style={styles.errorHint}>
          Make sure the backend is running:{"\n"}docker compose up
        </Text>
        <TouchableOpacity style={styles.retryButton} onPress={load}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
      }
    >
      <StatusBar style="light" />

      {/* Message */}
      <Text style={styles.message}>{data?.message}</Text>

      {/* Followed teams */}
      <Text style={styles.sectionTitle}>Following</Text>
      {data?.followed_teams.length === 0 ? (
        <Text style={styles.emptyText}>
          No teams followed yet. Go to Search to add some! 👆
        </Text>
      ) : (
        <FlatList
          data={data?.followed_teams}
          horizontal
          keyExtractor={(t) => t.id}
          renderItem={({ item }) => (
            <FollowedTeamChip team={item} onUnfollow={handleUnfollow} />
          )}
          contentContainerStyle={styles.chipRow}
          scrollEnabled={false}
        />
      )}

      {/* Fixtures */}
      <Text style={styles.sectionTitle}>Fixtures</Text>
      {data?.recent_fixtures.map((f) => (
        <FixtureCard key={f.id} fixture={f} />
      ))}

      {/* Standings */}
      <Text style={styles.sectionTitle}>Premier League</Text>
      {data && <StandingTable rows={data.standings} />}

      <View style={styles.footer} />
    </ScrollView>
  );
}

// ── Styles ───────────────────────────────────────────────────────

const C = {
  bg: "#0f172a",
  surface: "#1e293b",
  border: "#334155",
  text: "#f8fafc",
  muted: "#94a3b8",
  accent: "#3b82f6",
  green: "#22c55e",
  yellow: "#eab308",
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },
  center: {
    flex: 1, backgroundColor: C.bg,
    alignItems: "center", justifyContent: "center", padding: 24,
  },
  loadingText: { color: C.muted, marginTop: 12 },
  errorText: { color: "#f87171", fontSize: 16, textAlign: "center" },
  errorHint: { color: C.muted, marginTop: 8, textAlign: "center", lineHeight: 20 },
  retryButton: {
    marginTop: 16, backgroundColor: C.accent,
    paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8,
  },
  retryText: { color: "#fff", fontWeight: "600" },
  message: { color: C.muted, fontSize: 13, margin: 16, marginBottom: 4 },
  sectionTitle: {
    color: C.text, fontSize: 16, fontWeight: "700",
    marginHorizontal: 16, marginTop: 20, marginBottom: 8,
  },
  emptyText: { color: C.muted, marginHorizontal: 16, lineHeight: 20 },
  chipRow: { paddingHorizontal: 16, gap: 8 },
  chip: {
    flexDirection: "row", alignItems: "center", gap: 6,
    backgroundColor: C.surface, borderRadius: 20,
    paddingHorizontal: 12, paddingVertical: 8,
  },
  chipEmoji: { fontSize: 16 },
  chipName: { color: C.text, fontWeight: "600", fontSize: 13 },
  chipRemove: { color: C.muted, fontSize: 12, paddingLeft: 4 },
  card: {
    backgroundColor: C.surface, marginHorizontal: 16, marginBottom: 8,
    borderRadius: 10, padding: 12, borderWidth: 1, borderColor: C.border,
  },
  cardMeta: { color: C.muted, fontSize: 11, marginBottom: 6 },
  fixtureRow: { flexDirection: "row", alignItems: "center", gap: 8 },
  teamName: { color: C.text, flex: 1, fontSize: 14, fontWeight: "600" },
  textRight: { textAlign: "right" },
  score: {
    color: C.accent, fontWeight: "700", fontSize: 16,
    minWidth: 50, textAlign: "center",
  },
  finished: { color: C.green },
  scheduled: { color: C.yellow },
  table: {
    marginHorizontal: 16, backgroundColor: C.surface,
    borderRadius: 10, overflow: "hidden", borderWidth: 1, borderColor: C.border,
  },
  tableHeader: {
    flexDirection: "row", backgroundColor: "#0f172a",
    paddingVertical: 8, paddingHorizontal: 4,
  },
  tableRow: {
    flexDirection: "row", paddingVertical: 8,
    paddingHorizontal: 4, borderTopWidth: 1, borderTopColor: C.border,
  },
  tableCell: { color: C.muted, fontSize: 12, textAlign: "center", minWidth: 28 },
  tablePos: { minWidth: 24 },
  tableName: { flex: 1, textAlign: "left", color: C.text, paddingLeft: 4 },
  tablePts: { color: C.accent, fontWeight: "700" },
  footer: { height: 32 },
});

