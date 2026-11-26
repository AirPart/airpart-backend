import { describe, it, expect, vi, beforeEach } from "vitest";
import { httpRequest, ApiError } from "../http";

describe("HTTP Client (httpRequest)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("should send a request and return parsed JSON on success", async () => {
    const mockResponseData = { id: 1, name: "AirPart Item" };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        text: async () => JSON.stringify(mockResponseData),
      }),
    );

    const result = await httpRequest("/parts");

    expect(result).toEqual(mockResponseData);
    expect(fetch).toHaveBeenCalledWith(
      "/api/parts",
      expect.objectContaining({
        method: "GET",
        headers: { Accept: "application/json" },
      }),
    );
  });

  it("should throw ApiError when response is not ok", async () => {
    const errorPayload = { detail: "Unauthorized access" };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
        text: async () => JSON.stringify(errorPayload),
      }),
    );

    let caughtError: unknown;
    try {
      await httpRequest("/secure-data");
    } catch (error) {
      caughtError = error;
    }

    expect(caughtError).toBeInstanceOf(ApiError);
    if (caughtError instanceof ApiError) {
      expect(caughtError.status).toBe(401);
      expect(caughtError.message).toBe("Unauthorized access");
      expect(caughtError.payload).toEqual(errorPayload);
    }
  });
});
