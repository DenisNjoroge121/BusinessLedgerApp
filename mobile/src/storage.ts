import * as Crypto from "expo-crypto";
import * as SecureStore from "expo-secure-store";

const K = {
  access: "access_token",
  refresh: "refresh_token",
  pin: "pin_hash",
  salt: "pin_salt",
  bio: "biometric_enabled",
  device: "device_id",
  fails: "pin_fails",
};

export async function saveTokens(access: string, refresh?: string) {
  await SecureStore.setItemAsync(K.access, access);
  if (refresh) await SecureStore.setItemAsync(K.refresh, refresh);
}
export const getAccess = () => SecureStore.getItemAsync(K.access);
export const getRefresh = () => SecureStore.getItemAsync(K.refresh);

export async function getDeviceId() {
  let id = await SecureStore.getItemAsync(K.device);
  if (!id) {
    id = Crypto.randomUUID();
    await SecureStore.setItemAsync(K.device, id);
  }
  return id;
}

const hashPin = (pin: string, salt: string) =>
  Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, salt + pin);

export async function setPin(pin: string) {
  const salt = Crypto.randomUUID();
  await SecureStore.setItemAsync(K.salt, salt);
  await SecureStore.setItemAsync(K.pin, await hashPin(pin, salt));
}
export async function hasPin() {
  return !!(await SecureStore.getItemAsync(K.pin));
}
export async function verifyPin(pin: string) {
  const salt = await SecureStore.getItemAsync(K.salt);
  const saved = await SecureStore.getItemAsync(K.pin);
  if (!salt || !saved) return false;
  return (await hashPin(pin, salt)) === saved;
}

export async function getPinFails() {
  return Number((await SecureStore.getItemAsync(K.fails)) ?? "0");
}
export const setPinFails = (n: number) =>
  SecureStore.setItemAsync(K.fails, String(n));

export async function isBiometricEnabled() {
  return (await SecureStore.getItemAsync(K.bio)) === "1";
}
export const setBiometricEnabled = (on: boolean) =>
  SecureStore.setItemAsync(K.bio, on ? "1" : "0");

// Everything except the device id.
export async function clearAll() {
  for (const key of [K.access, K.refresh, K.pin, K.salt, K.bio, K.fails]) {
    await SecureStore.deleteItemAsync(key);
  }
}