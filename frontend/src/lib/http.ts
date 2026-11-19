const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "/api";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface HttpRequestInit {
  method?: HttpMethod;
  body?: unknown;
  accessToken?: string | null;
  signal?: AbortSignal;
}

export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

function parseJson(text: string): unknown {
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function extractErrorMessage(payload: unknown): string | null {
  if (typeof payload === "string") return payload;
  if (payload && typeof payload === "object") {
    const record = payload as Record<string, unknown>;
    if (typeof record.detail === "string") return record.detail;
    for (const value of Object.values(record)) {
      const message = extractErrorMessage(value);
      if (message) return message;
    }
  }
  return null;
}

export async function httpRequest<T>(
  path: string,
  init: HttpRequestInit = {},
): Promise<T> {
  const { method = "GET", body, accessToken, signal } = init;

  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

  const text = await response.text();
  const payload: unknown = text ? parseJson(text) : null;

  if (!response.ok) {
    throw new ApiError(
      response.status,
      extractErrorMessage(payload) ?? response.statusText,
      payload,
    );
  }

  return payload as T;
}
