import React, { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { PIN_LENGTH } from "../config";

type Props = {
  title: string;
  subtitle?: string;
  error?: string;
  onComplete: (pin: string) => void;
};

const ROWS = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "⌫"]];

export default function PinPad({ title, subtitle, error, onComplete }: Props) {
  const [pin, setPin] = useState("");

  const press = (key: string) => {
    if (key === "⌫") return setPin((p) => p.slice(0, -1));
    if (!key || pin.length >= PIN_LENGTH) return;
    const next = pin + key;
    if (next.length === PIN_LENGTH) {
      setPin("");
      onComplete(next);
    } else {
      setPin(next);
    }
  };

  return (
    <View style={s.wrap}>
      <Text style={s.title}>{title}</Text>
      {!!subtitle && <Text style={s.subtitle}>{subtitle}</Text>}
      <View style={s.dots}>
        {Array.from({ length: PIN_LENGTH }).map((_, i) => (
          <View key={i} style={[s.dot, i < pin.length && s.dotOn]} />
        ))}
      </View>
      <Text style={s.error}>{error ?? " "}</Text>
      {ROWS.map((row, r) => (
        <View key={r} style={s.row}>
          {row.map((key, c) => (
            <Pressable
              key={c}
              style={[s.key, !key && { opacity: 0 }]}
              onPress={() => press(key)}
              disabled={!key}
            >
              <Text style={s.keyText}>{key}</Text>
            </Pressable>
          ))}
        </View>
      ))}
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { alignItems: "center", paddingVertical: 24 },
  title: { fontSize: 22, fontWeight: "700", color: "#1b1b1b" },
  subtitle: { marginTop: 6, color: "#666" },
  dots: { flexDirection: "row", gap: 14, marginTop: 24 },
  dot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: "#2e7d32" },
  dotOn: { backgroundColor: "#2e7d32" },
  error: { color: "#c62828", marginVertical: 12, minHeight: 20, textAlign: "center" },
  row: { flexDirection: "row", gap: 18, marginBottom: 14 },
  key: {
    width: 72, height: 72, borderRadius: 36, backgroundColor: "#eef3ee",
    alignItems: "center", justifyContent: "center",
  },
  keyText: { fontSize: 26, color: "#1b1b1b" },
});