import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { UserMe } from "../types";
import { login as loginApi, logout as logoutApi, me as meApi, register as registerApi, RegisterPayload } from "../services/auth";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "../services/tokenStorage";

type AuthContextValue = {
  user: UserMe | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  reloadUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);

  async function reloadUser() {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      return;
    }
    const current = await meApi();
    setUser(current);
  }

  useEffect(() => {
    reloadUser().catch(() => {
      clearTokens();
      setUser(null);
    }).finally(() => setLoading(false));
  }, []);

  async function handleLogin(email: string, password: string, remember = true) {
    const tokens = await loginApi(email, password);
    setTokens(tokens.access_token, tokens.refresh_token, remember);
    await reloadUser();
  }

  async function handleRegister(payload: RegisterPayload) {
    const tokens = await registerApi(payload);
    setTokens(tokens.access_token, tokens.refresh_token, true);
    await reloadUser();
  }

  async function handleLogout() {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) {
        await logoutApi(refreshToken);
      }
    } finally {
      clearTokens();
      setUser(null);
    }
  }

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loading,
    isAuthenticated: Boolean(user),
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    reloadUser
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
}
