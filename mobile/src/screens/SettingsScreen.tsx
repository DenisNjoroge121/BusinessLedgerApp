import React, { useEffect, useState } from "react";
import { Alert, Pressable, StyleSheet, Switch, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../auth/AuthContext";
import { authenticateBiometric, biometricAvailable } from "../biometrics";
import * as storage from "../storage";

export default function SettingsScreen() {
  const { lock, logout } = useAuth();
  const [available, setAvailable] = useState(false);
  const [bio, setBio] = useState(false);

  useEffect(() => {
    (async () => {
      setAvailable(await biometricAvailable());
      setBio(await storage.isBiometricEnabled());
    })();
  }, []);

  const toggleBio = async (value: boolean) => {
    if (value && !(await authenticateBiometric())) return;
    await storage.setBiometricEnabled(value);
    setBio(value);
  };

  const confirmLogout = () =>
    Alert.alert("Log out?", "You will need your password and a new PIN next time.", [
      { text: "Cancel", style: "cancel" },
      { text: "Log out", style: "destructive", onPress: () => void logout() },
    ]);

  return (
    <SafeAreaView style={s.wrap}>
      <Text style={s.title}>Settings</Text>
      <View style={s.row}>
        <Text style={s.label}>
          Unlock with fingerprint / face{available ? "" : " (not set up on this phone)"}
        </Text>
        <Switch value={bio} onValueChange={toggleBio} disabled={!available} />
      </View>
      <Pressable style={s.button} onPress={lock}>
        <Text style={s.buttonText}>🔒 Lock now</Text>
      </Pressable>
      <Pressable style={[s.button, { backgroundColor: "#c62828" }]} onPress={confirmLogout}>
        <Text style={s.buttonText}>Log out</Text>
      </Pressable>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, padding: 24, backgroundColor: "#fff" },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 20 },
  row: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingVertical: 14, gap: 12,
  },
  label: { fontSize: 16, flex: 1 },
  button: {
    backgroundColor: "#2e7d32", padding: 15, borderRadius: 10,
    alignItems: "center", marginTop: 14,
  },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
});