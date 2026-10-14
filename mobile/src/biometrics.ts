import * as LocalAuthentication from "expo-local-authentication";

export async function biometricAvailable() {
  const hardware = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  return hardware && enrolled;
}

export async function authenticateBiometric() {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock Mom's Ledger",
    cancelLabel: "Use PIN",
    disableDeviceFallback: true,
  });
  return result.success;
}