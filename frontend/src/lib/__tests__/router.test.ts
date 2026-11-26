import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { navigate, usePathname } from "../router";

describe("Router Module", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    // ریست کردن URL مرورگر قبل از هر تست
    window.history.pushState({}, "", "/");
  });

  it("should update browser history and dispatch event on navigate", () => {
    const dispatchEventSpy = vi.spyOn(window, "dispatchEvent");
    const pushStateSpy = vi.spyOn(window.history, "pushState");

    navigate("/dashboard");

    expect(pushStateSpy).toHaveBeenCalledWith(null, "", "/dashboard");
    expect(dispatchEventSpy).toHaveBeenCalledTimes(1);
    const dispatchedEvent = dispatchEventSpy.mock.calls[0][0] as Event;
    expect(dispatchedEvent.type).toBe("app:routechange");
  });

  it("should not push state or dispatch event if path is identical to current path", () => {
    window.history.pushState({}, "", "/current");
    const pushStateSpy = vi.spyOn(window.history, "pushState");

    navigate("/current");

    expect(pushStateSpy).not.toHaveBeenCalled();
  });

  it("should track pathname changes using usePathname hook", () => {
    const { result } = renderHook(() => usePathname());

    expect(result.current).toBe("/");

    act(() => {
      navigate("/settings");
    });

    expect(result.current).toBe("/settings");
  });
});
