import React, {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
} from "react";
import * as api from "../api";
import { MAX_PIN_ATTEMPTS } from "../config";
import * as storage from "../storage";

export type Status = "loading" | "signedOut" | "needsPin" | "locked" | "unlocked"; //list all possible authentication states

type Ctx = { //Establish strict contract type, mapping exactly what state values and methods will be exposed to child component
  status: Status;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  createPin: (pin: string) => Promise<void>;
  unlockWithPin: (pin: string) => Promise<{ ok: boolean; attemptsLeft: number }>;
  unlockWithBiometric: () => Promise<boolean>;
  lock: () => void;
};

const AuthContext = createContext<Ctx>(null as unknown as Ctx); //Instantiates the react context object, assuring compiler that it will always be safely initialized later
export const useAuth = () => useContext(AuthContext); //Exposes a custom react hook so any child component can quickly consume the auth state


//Declares the provider component that wraps your app tree to supply the authentication lifecycle.
export function AuthProvider({ children }: { children: React.ReactNode }) { 
  const [status, setStatus] = useState<Status>("loading"); //sets the primary authentication state engine loading by default so that  app can check storage before deciding what screen to show

  // On launch: tokens present -> always start locked (or ask for a PIN).
  useEffect(() => {
    (async () => {
      const refresh = await storage.getRefresh(); //Checks for an existing session token.
      if (!refresh) return setStatus("signedOut");
      setStatus((await storage.hasPin()) ? "locked" : "needsPin"); //If a token exists, it checks if they've set up a security code.
    })();
  }, []);

  const logout = useCallback(async () => {
    await storage.clearAll();
    setStatus("signedOut");
  }, []); //• memoized callback that wipes out local security tokens, resets local auth variables, and drops the state to "signedOut" to force the login interface to appear.

  useEffect(() => {
    api.setAuthFailureHandler(() => void logout());
    return () => api.setAuthFailureHandler(null);
  }, [logout]); //If any network request returns a 401 Unauthorized response elsewhere in your app, this handler intercepts it and automatically triggers your logout() function.

  const login = useCallback(async (username: string, password: string) => {
    const t = await api.login(username.trim(), password); //Authenticate the credential against the backend
    await storage.saveTokens(t.access, t.refresh); //securely caches and refresh tokens locally
    await storage.setPinFails(0); //restores incorrect passcode counter back to zero
    setStatus((await storage.hasPin()) ? "unlocked" : "needsPin"); // determines whether to put user directly into app or initialize a pin
  }, []);

  const createPin = useCallback(async (pin: string) => {
    await storage.setPin(pin);
    await storage.setPinFails(0);
    setStatus("unlocked");
  }, []); //Takes a newly created PIN string, saves it to storage, resets the failure counter, and signs the user completely into the app

  const unlockWithPin = useCallback(
    async (pin: string) => {
      const fails = await storage.getPinFails();
      if (fails >= MAX_PIN_ATTEMPTS) {
        await logout();
        return { ok: false, attemptsLeft: 0 };
      }
      if (await storage.verifyPin(pin)) {
        await storage.setPinFails(0);
        setStatus("unlocked");
        return { ok: true, attemptsLeft: MAX_PIN_ATTEMPTS };
      }
      const n = fails + 1;
      await storage.setPinFails(n);
      if (n >= MAX_PIN_ATTEMPTS) {
        await logout();
        return { ok: false, attemptsLeft: 0 };
      }
      return { ok: false, attemptsLeft: MAX_PIN_ATTEMPTS - n };
    },
    [logout]
  );

  const unlockWithBiometric = useCallback(async () => {
    const { authenticateBiometric } = await import("../biometrics");
    if (await authenticateBiometric()) {
      await storage.setPinFails(0);
      setStatus("unlocked");
      return true;
    }
    return false;
  }, []);

  const lock = useCallback(() => {
    setStatus((s) => (s === "unlocked" ? "locked" : s));
  }, []);

  const value = useMemo(
    () => ({ status, login, logout, createPin, unlockWithPin, unlockWithBiometric, lock }),
    [status, login, logout, createPin, unlockWithPin, unlockWithBiometric, lock]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}