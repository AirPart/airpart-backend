import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ChangePasswordForm } from "../ChangePasswordForm";
import * as SecurityApiModule from "../security-api";
import { ApiError } from "../../../lib/http";

vi.mock("../security-api", () => ({
  changePasswordRequest: vi.fn(),
}));

describe("ChangePasswordForm Component", () => {
  const mockChangePassword = vi.mocked(SecurityApiModule.changePasswordRequest);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render form elements and show validation errors when submitted empty", async () => {
    render(<ChangePasswordForm />);

    expect(
      screen.getByRole("heading", { name: /تغییر رمز عبور/i }),
    ).toBeInTheDocument();

    const submitButton = screen.getByRole("button", {
      name: /به‌روزرسانی کلمه عبور/i,
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/رمز عبور فعلی الزامی است/i)).toBeInTheDocument();
      expect(screen.getByText(/رمز عبور جدید الزامی است/i)).toBeInTheDocument();
    });

    expect(mockChangePassword).not.toHaveBeenCalled();
  });

  it("should validate minimum length for new password", async () => {
    render(<ChangePasswordForm />);

    const oldPasswordInput = screen.getByLabelText(/رمز عبور فعلی/i);
    const newPasswordInput = screen.getByLabelText(/رمز عبور جدید/i);
    const submitButton = screen.getByRole("button", {
      name: /به‌روزرسانی کلمه عبور/i,
    });

    fireEvent.change(oldPasswordInput, { target: { value: "oldpass123" } });
    fireEvent.change(newPasswordInput, { target: { value: "short" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/رمز عبور جدید باید حداقل ۸ کاراکتر باشد/i),
      ).toBeInTheDocument();
    });

    expect(mockChangePassword).not.toHaveBeenCalled();
  });

  it("should submit successfully and show success message on valid inputs", async () => {
    mockChangePassword.mockResolvedValueOnce(undefined);

    render(<ChangePasswordForm />);

    fireEvent.change(screen.getByLabelText(/رمز عبور فعلی/i), {
      target: { value: "oldpassword123" },
    });
    fireEvent.change(screen.getByLabelText(/رمز عبور جدید/i), {
      target: { value: "newsecurepassword99" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: /به‌روزرسانی کلمه عبور/i }),
    );

    await waitFor(() => {
      expect(mockChangePassword).toHaveBeenCalledWith({
        old_password: "oldpassword123",
        new_password: "newsecurepassword99",
      });
    });

    expect(
      await screen.findByText(/رمز عبور شما با موفقیت به‌روزرسانی شد/i),
    ).toBeInTheDocument();
  });

  it("should handle ApiError 400 and display server validation errors", async () => {
    const errorPayload = { old_password: ["رمز عبور فعلی نادرست است."] };
    mockChangePassword.mockRejectedValueOnce(
      new ApiError(400, "Bad Request", errorPayload),
    );

    render(<ChangePasswordForm />);

    fireEvent.change(screen.getByLabelText(/رمز عبور فعلی/i), {
      target: { value: "wrongoldpass" },
    });
    fireEvent.change(screen.getByLabelText(/رمز عبور جدید/i), {
      target: { value: "newsecurepassword99" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: /به‌روزرسانی کلمه عبور/i }),
    );

    await waitFor(() => {
      expect(screen.getByText(/رمز عبور فعلی نادرست است/i)).toBeInTheDocument();
    });
  });
});
