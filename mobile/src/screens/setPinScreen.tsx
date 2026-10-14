import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../auth/AuthContext";
import PinPad from "../components/PinPad";

export default function SetPinScreen() {
  const { createPin } = useAuth();
  const [first, setFirst] = useState<string | null>(null);
  const [error, setError] = useState("");

  const onComplete = (pin: string) => {
    if (first === null) {
      setFirst(pin);
      setError("");
    } else if (pin === first) {
      void createPin(pin);
    } else {
      setFirst(null);
      setError("PINs did not match. Start again.");
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff", justifyContent: "center" }}>
      <PinPad
        title={first === null ? "Create a 6-digit PIN" : "Confirm your PIN"}
        subtitle="This PIN unlocks the app on this phone"
        error={error}
        onComplete={onComplete}
      />
    </SafeAreaView>
  );
}