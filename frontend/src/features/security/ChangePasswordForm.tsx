import { useState, type FormEvent } from "react";
import { ApiError } from "../../lib/http";
import {
  changePasswordRequest,
  type ChangePasswordErrorResponse,
} from "./security-api";

interface FieldErrors {
  old_password?: string;
  new_password?: string;
  general?: string;
}

export function ChangePasswordForm() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errors, setErrors] = useState<FieldErrors>({});

  const validate = (): boolean => {
    const nextErrors: FieldErrors = {};

    if (!oldPassword.trim()) {
      nextErrors.old_password = "رمز عبور فعلی الزامی است.";
    }
    if (!newPassword.trim()) {
      nextErrors.new_password = "رمز عبور جدید الزامی است.";
    } else if (newPassword.length < 8) {
      nextErrors.new_password = "رمز عبور جدید باید حداقل ۸ کاراکتر باشد.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccessMessage(null);
    setErrors({});

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      await changePasswordRequest({
        old_password: oldPassword,
        new_password: newPassword,
      });

      // پاسخ 204 No Content موفق
      setSuccessMessage("رمز عبور شما با موفقیت به‌روزرسانی شد.");
      setOldPassword("");
      setNewPassword("");
    } catch (error) {
      if (error instanceof ApiError) {
        const payload = error.payload as
          | ChangePasswordErrorResponse
          | undefined;

        if (error.status === 400 && payload) {
          setErrors({
            old_password: payload.old_password?.[0],
            new_password: payload.new_password?.[0],
            general:
              payload.detail ||
              payload.non_field_errors?.[0] ||
              (payload.old_password || payload.new_password
                ? undefined
                : "اطلاعات ارسالی نامعتبر است."),
          });
          return;
        }

        if (error.status === 401) {
          setErrors({
            general: "نشست شما منقضی شده است. لطفاً مجدداً وارد سیستم شوید.",
          });
          return;
        }

        setErrors({
          general:
            (payload && payload.detail) ||
            "خطایی در برقراری ارتباط با سرور رخ داده است.",
        });
      } else {
        setErrors({ general: "خطای ناشناخته رخ داده است." });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>تغییر رمز عبور</h3>

      {successMessage && (
        <div
          style={{
            padding: "0.75rem 1rem",
            marginBottom: "1rem",
            backgroundColor: "#e6ffed",
            color: "#155724",
            border: "1px solid #c3e6cb",
            borderRadius: "4px",
          }}
        >
          {successMessage}
        </div>
      )}

      {errors.general && (
        <div
          style={{
            padding: "0.75rem 1rem",
            marginBottom: "1rem",
            backgroundColor: "#ffeef0",
            color: "#86181d",
            border: "1px solid #fdaeb7",
            borderRadius: "4px",
          }}
        >
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label
            htmlFor="old_password"
            style={{
              display: "block",
              marginBottom: "0.25rem",
              fontWeight: 500,
            }}
          >
            رمز عبور فعلی
          </label>
          <input
            id="old_password"
            type="password"
            autoComplete="current-password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.5rem",
              borderRadius: "4px",
              border: errors.old_password
                ? "1px solid #d73a49"
                : "1px solid #ccc",
              boxSizing: "border-box",
            }}
          />
          {errors.old_password && (
            <span
              style={{
                color: "#d73a49",
                fontSize: "0.85rem",
                marginTop: "0.25rem",
                display: "block",
              }}
            >
              {errors.old_password}
            </span>
          )}
        </div>

        <div style={{ marginBottom: "1.25rem" }}>
          <label
            htmlFor="new_password"
            style={{
              display: "block",
              marginBottom: "0.25rem",
              fontWeight: 500,
            }}
          >
            رمز عبور جدید
          </label>
          <input
            id="new_password"
            type="password"
            autoComplete="new-password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.5rem",
              borderRadius: "4px",
              border: errors.new_password
                ? "1px solid #d73a49"
                : "1px solid #ccc",
              boxSizing: "border-box",
            }}
          />
          {errors.new_password && (
            <span
              style={{
                color: "#d73a49",
                fontSize: "0.85rem",
                marginTop: "0.25rem",
                display: "block",
              }}
            >
              {errors.new_password}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.5rem 1.25rem",
            backgroundColor: loading ? "#6c757d" : "#0056b3",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 500,
          }}
        >
          {loading ? "در حال ذخیره‌سازی..." : "به‌روزرسانی کلمه عبور"}
        </button>
      </form>
    </div>
  );
}
