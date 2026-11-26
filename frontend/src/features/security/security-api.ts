import { api } from "../../lib/api-client";

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export interface ChangePasswordErrorResponse {
  old_password?: string[];
  new_password?: string[];
  detail?: string;
  non_field_errors?: string[];
}

export async function changePasswordRequest(
  payload: ChangePasswordPayload,
): Promise<void> {
  await api.post<void>("/auth/change-password", payload);
}
