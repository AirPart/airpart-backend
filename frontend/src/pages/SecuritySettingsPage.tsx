import { ChangePasswordForm } from "../features/security/ChangePasswordForm";
import { navigate } from "../lib/router";

export function SecuritySettingsPage() {
  return (
    <div
      style={{
        maxWidth: "650px",
        margin: "3rem auto",
        padding: "0 1.5rem",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
          borderBottom: "1px solid #e1e4e8",
          paddingBottom: "1rem",
        }}
      >
        <div>
          <h2 style={{ margin: 0, color: "#24292e" }}>تنظیمات امنیتی</h2>
          <p
            style={{
              margin: "0.25rem 0 0 0",
              color: "#586069",
              fontSize: "0.9rem",
            }}
          >
            مدیریت رمز عبور و تنظیمات دسترسی حساب کاربری هوانوردی
          </p>
        </div>
        <button
          onClick={() => navigate("/")}
          style={{
            padding: "0.45rem 0.9rem",
            backgroundColor: "#f6f8fa",
            color: "#24292e",
            border: "1px solid rgba(27, 31, 35, 0.15)",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: 500,
            fontSize: "0.85rem",
          }}
        >
          بازگشت به داشبورد
        </button>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <ChangePasswordForm />
      </div>
    </div>
  );
}
