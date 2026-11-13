import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api, ApiError, getToken, setToken, type User } from "../lib/api";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  unavailable: boolean;
  retry: () => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [loading, setLoading] = useState(true);
  const [unavailable, setUnavailable] = useState(false);
  const [bootAttempt, setBootAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    const existing = getToken();
    setLoading(true);
    setUnavailable(false);

    if (!existing) {
      setLoading(false);
      return;
    }

    api
      .me()
      .then((profile) => {
        if (active) setUser(profile);
      })
      .catch((error: unknown) => {
        if (!active) return;
        if (error instanceof ApiError && error.status === 0) {
          // Keep the token: the session may still be valid once the service is back.
          setUnavailable(true);
          return;
        }
        setToken(null);
        setTokenState(null);
        setUser(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [bootAttempt]);

  const retry = useCallback(() => setBootAttempt((value) => value + 1), []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await api.login(email, password);
    setToken(response.access_token);
    setTokenState(response.access_token);
    setUser(response.user);
    setUnavailable(false);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setTokenState(null);
    setUser(null);
    setUnavailable(false);
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, unavailable, retry, login, logout }),
    [user, token, loading, unavailable, retry, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return context;
}
