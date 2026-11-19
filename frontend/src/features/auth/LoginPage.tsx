import { useState, type FormEvent } from "react";
import { ApiError } from "../../lib/http";
import { useAuth } from "./AuthContext";

function toLoginErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return "نام کاربری یا رمز عبور نادرست است.";
    if (error.status >= 500) return "خطای سرور. لطفاً بعداً دوباره تلاش کنید.";
    return error.message;
  }
  return "ارتباط با سرور برقرار نشد. اتصال شبکه را بررسی کنید.";
}

export function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await login(username.trim(), password);
    } catch (err) {
      setError(toLoginErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="centered">
      <form className="card" onSubmit={handleSubmit} noValidate>
        <h1>ورود به سامانه</h1>
        <p className="muted">سامانه‌ی داخلی AirPart</p>

        <label htmlFor="username">نام کاربری</label>
        <input
          id="username"
          name="username"
          autoComplete="username"
          autoFocus
          required
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          disabled={submitting}
        />

        <label htmlFor="password">رمز عبور</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          disabled={submitting}
        />

        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={submitting || !username.trim() || !password}
        >
          {submitting ? "در حال ورود…" : "ورود"}
        </button>
      </form>
    </main>
  );
}
