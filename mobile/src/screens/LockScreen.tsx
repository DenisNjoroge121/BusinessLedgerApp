import React, { useEffect, useState } from "react";
import { Alert, Pressable, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../auth/AuthContext";
import { biometricAvailable } from "../biometrics";
import PinPad from "../components/PinPad";
import * as storage from "../storage";

export default function LockScreen() {
  const { unlockWithPin, unlockWithBiometric } = useAuth();
  const [error, setError] = useState("");
  const [bio, setBio] = useState(false);

  useEffect(() => {
    (async () => {
      const on = (await storage.isBiometricEnabled()) && (await biometricAvailable());
      setBio(on);
      if (on) void unlockWithBiometric();
    })();
  }, [unlockWithBiometric]);

  const onComplete = async (pin: string) => {
    const r = await unlockWithPin(pin);
    if (r.ok) return;
    if (r.attemptsLeft === 0) {
      Alert.alert("Too many wrong PINs", "Please log in again with your password.");
      return;
    }
    setError(`Wrong PIN. ${r.attemptsLeft} attempt(s) left.`);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff", justifyContent: "center" }}>
      <PinPad
        title="Enter your PIN"
        subtitle="Mom's Ledger is locked"
        error={error}
        onComplete={onComplete}
      />
      {bio && (
        <Pressable onPress={() => void unlockWithBiometric()} style={{ alignItems: "center" }}>
          <Text style={{ color: "#2e7d32", fontSize: 16 }}>Use fingerprint / face</Text>
        </Pressable>
      )}
    </SafeAreaView>
  );
}