import { useAuth } from "../features/auth/AuthContext";

export function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <main className="page">
      <header className="topbar">
        <h1>داشبورد</h1>
        <button type="button" onClick={logout}>
          خروج
        </button>
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
