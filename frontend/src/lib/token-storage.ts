const REFRESH_TOKEN_KEY = "airpart.refresh_token";

export const tokenStorage = {
  getRefreshToken(): string | null {
    try {
      return window.sessionStorage.getItem(REFRESH_TOKEN_KEY);
    } catch {
      return null;
    }
  },

  setRefreshToken(token: string): void {
    try {
      window.sessionStorage.setItem(REFRESH_TOKEN_KEY, token);
    } catch {}
  },

  clear(): void {
    try {
      window.sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    } catch {}
  },
};
