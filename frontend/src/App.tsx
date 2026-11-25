import { LoginPage } from "./features/auth/LoginPage";
import { useAuth } from "./features/auth/AuthContext";
import { usePathname } from "./lib/router";
import { DashboardPage } from "./pages/DashboardPage";
import { SecuritySettingsPage } from "./pages/SecuritySettingsPage";

export function App() {
  const { status } = useAuth();
  const pathname = usePathname();

  if (status === "loading") {
    return <main className="centered">در حال بارگذاری…</main>;
  }

  if (status === "anonymous") {
    return <LoginPage />;
  }

  if (pathname === "/settings/security") {
    return <SecuritySettingsPage />;
  }

  return <DashboardPage />;
}
