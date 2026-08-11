import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { api, setAuthToken } from "../../api/client";
import type { AuthUser } from "../../api/types";
import { loadToken, TOKEN_STORAGE_KEY } from "./session";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readToken(): string | null {
  if (typeof window === "undefined") return null;
  return loadToken(window.localStorage.getItem(TOKEN_STORAGE_KEY));
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(readToken);
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    setAuthToken(token);
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
      api.me().then(setUser).catch(() => {
        // token invalid/expired — clear it
        setToken(null);
        setUser(null);
      });
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      setUser(null);
    }
  }, [token]);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.login(email, password);
    setToken(access_token);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    await api.register(email, password);
    const { access_token } = await api.login(email, password);
    setToken(access_token);
  }, []);

  const logout = useCallback(() => setToken(null), []);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
