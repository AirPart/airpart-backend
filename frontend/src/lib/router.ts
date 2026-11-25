import { useState, useEffect } from "react";

const ROUTE_CHANGE_EVENT = "app:routechange";

export function navigate(path: string): void {
  if (window.location.pathname === path) {
    return;
  }
  window.history.pushState(null, "", path);
  window.dispatchEvent(new Event(ROUTE_CHANGE_EVENT));
}

export function usePathname(): string {
  const [pathname, setPathname] = useState<string>(
    () => window.location.pathname,
  );

  useEffect(() => {
    const handleLocationChange = () => {
      setPathname(window.location.pathname);
    };

    window.addEventListener("popstate", handleLocationChange);
    window.addEventListener(ROUTE_CHANGE_EVENT, handleLocationChange);

    return () => {
      window.removeEventListener("popstate", handleLocationChange);
      window.removeEventListener(ROUTE_CHANGE_EVENT, handleLocationChange);
    };
  }, []);

  return pathname;
}
