import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginPage } from "../LoginPage";
import * as AuthContextModule from "../AuthContext";
import { ApiError } from "../../../lib/http";

vi.mock("../AuthContext", () => ({
  useAuth: vi.fn(),
}));

describe("LoginPage Component", () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(AuthContextModule, "useAuth").mockReturnValue({
      login: mockLogin,
      user: null,
      logout: vi.fn(),
    } as any);
  });

  it("should render login form fields and submit successfully", async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    render(<LoginPage />);

    expect(
      screen.getByRole("heading", { name: /ورود به سامانه/i }),
    ).toBeInTheDocument();

    const usernameInput = screen.getByLabelText(/نام کاربری/i);
    const passwordInput = screen.getByLabelText(/رمز عبور/i);
    const submitButton = screen.getByRole("button", { name: /ورود/i });

    expect(submitButton).toBeDisabled(); // چون فرم خالی است

    fireEvent.change(usernameInput, { target: { value: "pilot_mamad" } });
    fireEvent.change(passwordInput, {
      target: { value: "secure-password123" },
    });

    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    expect(submitButton).toHaveTextContent(/در حال ورود…/i);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(
        "pilot_mamad",
        "secure-password123",
      );
    });
  });

  it("should display correct error message when login fails with 401 Unauthorized", async () => {
    mockLogin.mockRejectedValueOnce(new ApiError(401, "Unauthorized", {}));

    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/نام کاربری/i), {
      target: { value: "wrong_user" },
    });
    fireEvent.change(screen.getByLabelText(/رمز عبور/i), {
      target: { value: "wrong_pass" },
    });

    fireEvent.click(screen.getByRole("button", { name: /ورود/i }));

    const errorMessage = await screen.findByRole("alert");
    expect(errorMessage).toHaveTextContent(
      "نام کاربری یا رمز عبور نادرست است.",
    );
  });
});
