import React, { useState } from "react";
import { ActivityIndicator, KeyboardAvoidingView, Platform, Pressable, StyleSheet, Text, TextInput,} from "react-native";

import { useAuth } from "../auth/AuthContext";

export default function LoginScreen() {
    const { login } = useAuth();
    const [ username, setUsername ] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    const submit = async () => {
        if (!username || !password) return setError("Enter your username and password.");
        setBusy(true);
        setError("");

        try{
            await login(username, password);
        } catch (e: any) {
            setError(
                e?.status ? e.message : "Cannot reach the server. Check your internet connection."
            );
            setBusy(false);
        }
    };

    return (
        <KeyboardAvoidingView style={s.wrap} behavior={Platform.OS === "ios" ? "padding" : undefined} >
            <Text style={s.logo}>📒</Text>
            <Text style={s.title}>Mom's Ledger</Text>
            <TextInput 
                style={s.input} 
                placeholder="Username" autoCapitalize="none"
                autoCorrect={false}
                value={username}
                onChangeText={setUsername}
            />
            <TextInput
                style={s.input}
                placeholder="Password"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
                onSubmitEditing={submit}
            />

            {!!error && <Text style={s.error}>{error}</Text>}
            <Pressable style={s.button} onPress={submit} disabled={busy}>
                {busy ? <ActivityIndicator color="#fff" /> : <Text style={s.buttonText}>Log in</Text>}
            </Pressable>
        </KeyboardAvoidingView>
    )
}

const s = StyleSheet.create({
  wrap: { flex: 1, justifyContent: "center", padding: 28, backgroundColor: "#fff" },
  logo: { fontSize: 56, textAlign: "center" },
  title: { fontSize: 28, fontWeight: "700", textAlign: "center", marginBottom: 28 },
  input: {
    borderWidth: 1, borderColor: "#cfd8cf", borderRadius: 10,
    padding: 14, fontSize: 16, marginBottom: 14,
  },
  error: { color: "#c62828", marginBottom: 12 },
  button: { backgroundColor: "#2e7d32", padding: 16, borderRadius: 10, alignItems: "center" },
  buttonText: { color: "#fff", fontSize: 17, fontWeight: "600" },
});