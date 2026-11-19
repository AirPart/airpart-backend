import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { UserDto } from "@airpart/api-types";
import { refreshAccessToken, setAccessToken } from "../../lib/api-client";
import { tokenStorage } from "../../lib/token-storage";
import { fetchCurrentUser, loginRequest } from "./auth-api";

type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  status: AuthStatus;
  user: UserDto | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<UserDto | null>(null);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      const token = await refreshAccessToken();
      if (cancelled) return;

      if (!token) {
        setStatus("anonymous");
        return;
      }

      try {
        const me = await fetchCurrentUser(token);
        if (cancelled) return;
        setUser(me);
        setStatus("authenticated");
      } catch {
        if (cancelled) return;
        setAccessToken(null);
        tokenStorage.clear();
        setStatus("anonymous");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const tokens = await loginRequest({ username, password });
    setAccessToken(tokens.access);
    tokenStorage.setRefreshToken(tokens.refresh);

    const me = await fetchCurrentUser(tokens.access);
    setUser(me);
    setStatus("authenticated");
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    tokenStorage.clear();
    setUser(null);
    setStatus("anonymous");
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, login, logout }),
    [status, user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within <AuthProvider>");
  return context;
}
