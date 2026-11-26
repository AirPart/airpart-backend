import { useAuth } from "../features/auth/AuthContext";
import { navigate } from "../lib/router";

export function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <main className="page">
      <header className="topbar">
        <h1>داشبورد</h1>

        <div className="topbar-actions">
          <button type="button" onClick={() => navigate("/settings/security")}>
            تنظیمات امنیتی
          </button>

          <button type="button" onClick={logout}>
            خروج
          </button>
        </div>
      </header>

      <section className="card">
        <h2>کاربر جاری</h2>

        <dl>
          <dt>نام کاربری</dt>
          <dd>{user?.username}</dd>

          <dt>ایمیل</dt>
          <dd>{user?.email}</dd>

          <dt>نقش</dt>
          <dd>{user?.role}</dd>

          <dt>دامنه</dt>
          <dd>{user?.domain}</dd>
        </dl>
      </section>
    </main>
  );
}
