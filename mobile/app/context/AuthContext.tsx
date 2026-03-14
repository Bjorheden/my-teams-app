// mobile/app/context/AuthContext.tsx
// ─────────────────────────────────────────────────────────────────
// LEARNING NOTE – React Context for auth state
//
// Context is React's way of sharing state without prop-drilling.
// Instead of passing `token` through every component, we provide it
// once here and any component can read it with `useAuth()`.
//
// Lifecycle:
//   1. App starts  → `isLoading=true`, try to restore token from SecureStore
//   2. Token found → set in memory + context → user goes to tabs
//   3. No token    → `isLoading=false` → user sees login screen
//   4. Login/Register → server returns token → save to SecureStore + context
//   5. Logout      → delete from SecureStore, clear context
//
// LEARNING NOTE – SecureStore
//   expo-secure-store encrypts values using the device's secure enclave
//   (Keychain on iOS, Keystore on Android). Much safer than AsyncStorage
//   which stores values in plain text.
// ─────────────────────────────────────────────────────────────────

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import * as SecureStore from "expo-secure-store";

import { setToken, setOnUnauthorized } from "../api/client";

const TOKEN_KEY = "myteams_access_token";

interface AuthContextValue {
  token: string | null;
  isLoading: boolean;
  saveToken: (token: string) => Promise<void>;
  clearToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Define clearToken first so saveToken can reference it in its deps.
  const clearToken = useCallback(async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setToken(null);
    setOnUnauthorized(null);
    setTokenState(null);
  }, []);

  const saveToken = useCallback(async (newToken: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, newToken);
    setToken(newToken);
    setOnUnauthorized(clearToken);
    setTokenState(newToken);
  }, [clearToken]);

  // On mount: try to restore previous session from SecureStore
  useEffect(() => {
    (async () => {
      try {
        const stored = await SecureStore.getItemAsync(TOKEN_KEY);
        if (stored) {
          setToken(stored);              // update the API client module
          setOnUnauthorized(clearToken); // auto-logout on 401
          setTokenState(stored);         // update context state
        }
      } catch {
        // SecureStore unavailable (e.g. running in web/Expo Go without native)
        // Silently ignore – user will just see the login screen
      } finally {
        setIsLoading(false);
      }
    })();
  }, [clearToken]);

  return (
    <AuthContext.Provider value={{ token, isLoading, saveToken, clearToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
