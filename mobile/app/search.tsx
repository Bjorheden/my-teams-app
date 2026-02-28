// mobile/app/search.tsx – Team Search screen

import { useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { followTeam, searchTeams } from "./api/client";
import type { Team } from "./types";

// ── Sub-components ───────────────────────────────────────────────

function TeamRow({
  team,
  onFollow,
  feedback,
}: {
  team: Team;
  onFollow: (id: string) => void;
  feedback: Record<string, string>;
}) {
  const msg = feedback[team.id];
  return (
    <View style={styles.row}>
      <Text style={styles.crest}>{team.crest_emoji}</Text>
      <View style={styles.rowInfo}>
        <Text style={styles.rowName}>{team.name}</Text>
        <Text style={styles.rowMeta}>
          {team.league} · {team.country}
        </Text>
      </View>
      <TouchableOpacity
        style={[styles.followBtn, msg === "✓" && styles.followedBtn]}
        onPress={() => onFollow(team.id)}
      >
        <Text style={styles.followBtnText}>{msg ?? "+ Follow"}</Text>
      </TouchableOpacity>
    </View>
  );
}

// ── Main screen ──────────────────────────────────────────────────

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  // Maps team_id → short feedback message ("✓" or "Already following")
  const [feedback, setFeedback] = useState<Record<string, string>>({});

  const handleSearch = async () => {
    if (query.trim() === "") return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const res = await searchTeams(query.trim(), 20);
      setResults(res.results);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (teamId: string) => {
    try {
      await followTeam(teamId);
      setFeedback((prev) => ({ ...prev, [teamId]: "✓" }));
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error";
      // "Already following" comes from the 409 detail
      setFeedback((prev) => ({
        ...prev,
        [teamId]: msg.includes("Already") ? "Following" : "Error",
      }));
    }
  };

  return (
    <View style={styles.container}>
      {/* Search bar */}
      <View style={styles.searchBar}>
        <TextInput
          style={styles.input}
          placeholder="Search by name, country, league…"
          placeholderTextColor="#64748b"
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TouchableOpacity style={styles.searchBtn} onPress={handleSearch}>
          <Text style={styles.searchBtnText}>Search</Text>
        </TouchableOpacity>
      </View>

      {/* Hint */}
      {!searched && (
        <Text style={styles.hint}>
          Try: "Arsenal", "Spain", "Bundesliga"
        </Text>
      )}

      {/* Loading */}
      {loading && (
        <ActivityIndicator
          size="large"
          color="#3b82f6"
          style={{ marginTop: 32 }}
        />
      )}

      {/* Error */}
      {error && <Text style={styles.errorText}>⚠️ {error}</Text>}

      {/* Results */}
      <FlatList
        data={results}
        keyExtractor={(t) => t.id}
        renderItem={({ item }) => (
          <TeamRow team={item} onFollow={handleFollow} feedback={feedback} />
        )}
        ListEmptyComponent={
          searched && !loading ? (
            <Text style={styles.emptyText}>No teams found for "{query}"</Text>
          ) : null
        }
        contentContainerStyle={{ paddingBottom: 32 }}
      />
    </View>
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
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },
  searchBar: {
    flexDirection: "row", gap: 8,
    margin: 16, marginBottom: 8,
  },
  input: {
    flex: 1, backgroundColor: C.surface, color: C.text,
    borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10,
    fontSize: 15, borderWidth: 1, borderColor: C.border,
  },
  searchBtn: {
    backgroundColor: C.accent, borderRadius: 10,
    paddingHorizontal: 16, justifyContent: "center",
  },
  searchBtnText: { color: "#fff", fontWeight: "700" },
  hint: { color: C.muted, fontSize: 13, marginHorizontal: 16, marginBottom: 8 },
  errorText: { color: "#f87171", margin: 16 },
  emptyText: { color: C.muted, textAlign: "center", marginTop: 32 },
  row: {
    flexDirection: "row", alignItems: "center", gap: 12,
    backgroundColor: C.surface, marginHorizontal: 16, marginBottom: 8,
    borderRadius: 10, padding: 12, borderWidth: 1, borderColor: C.border,
  },
  crest: { fontSize: 28 },
  rowInfo: { flex: 1 },
  rowName: { color: C.text, fontWeight: "600", fontSize: 15 },
  rowMeta: { color: C.muted, fontSize: 12, marginTop: 2 },
  followBtn: {
    backgroundColor: C.accent, borderRadius: 8,
    paddingHorizontal: 12, paddingVertical: 6,
  },
  followedBtn: { backgroundColor: "#16a34a" },
  followBtnText: { color: "#fff", fontSize: 13, fontWeight: "700" },
});
