import type { RefreshRequestDto, TokenResponseDto } from "@airpart/api-types";
import { ApiError, httpRequest, type HttpRequestInit } from "./http";
import { tokenStorage } from "./token-storage";

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  const refresh = tokenStorage.getRefreshToken();
  if (!refresh) return null;

  const body: RefreshRequestDto = { refresh };

  refreshPromise = httpRequest<TokenResponseDto>("/auth/refresh", {
    method: "POST",
    body,
  })
    .then((tokens) => {
      accessToken = tokens.access;
      if (tokens.refresh) tokenStorage.setRefreshToken(tokens.refresh);
      return tokens.access;
    })
    .catch(() => {
      accessToken = null;
      tokenStorage.clear();
      return null;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

async function request<T>(path: string, init: HttpRequestInit): Promise<T> {
  try {
    return await httpRequest<T>(path, { ...init, accessToken });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;

    const renewed = await refreshAccessToken();
    if (!renewed) throw error;

    return httpRequest<T>(path, { ...init, accessToken: renewed });
  }
}

export const api = {
  get<T>(path: string, init: Omit<HttpRequestInit, "method" | "body"> = {}) {
    return request<T>(path, { ...init, method: "GET" });
  },
  post<T>(
    path: string,
    body?: unknown,
    init: Omit<HttpRequestInit, "method" | "body"> = {},
  ) {
    return request<T>(path, { ...init, method: "POST", body });
  },
};
