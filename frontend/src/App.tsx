import { LoginPage } from "./features/auth/LoginPage";
import { useAuth } from "./features/auth/AuthContext";
import { DashboardPage } from "./pages/DashboardPage";

export function App() {
  const { status } = useAuth();

  if (status === "loading") {
    return <main className="centered">در حال بارگذاری…</main>;
  }

  return status === "authenticated" ? <DashboardPage /> : <LoginPage />;
}
