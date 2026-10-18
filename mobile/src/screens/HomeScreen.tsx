import React, { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as api from "../api";

export default function HomeScreen() {
  const [me, setMe] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.me().then(setMe).catch((e) => setError(e.message));
  }, []);

  return (
    <SafeAreaView style={s.wrap}>
      <Text style={s.title}>Welcome{me ? `, ${me.username}` : ""} 👋</Text>
      {me && (
        <View style={s.card}>
          <Text style={s.line}>Business: {me.business_name}</Text>
          <Text style={s.line}>Role: {me.role}</Text>
        </View>
      )}
      {!!error && <Text style={{ color: "#c62828" }}>{error}</Text>}
      <Text style={s.note}>The dashboard, categories and customers arrive in Phase 5.</Text>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, padding: 24, backgroundColor: "#fff" },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 16 },
  card: { backgroundColor: "#eef3ee", padding: 16, borderRadius: 12, marginBottom: 16 },
  line: { fontSize: 16, marginBottom: 4 },
  note: { color: "#666", marginTop: 8 },
});