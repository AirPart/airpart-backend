import type {
  LoginRequestDto,
  TokenResponseDto,
  UserDto,
} from "@airpart/api-types";
import { httpRequest } from "../../lib/http";

export function loginRequest(
  credentials: LoginRequestDto,
): Promise<TokenResponseDto> {
  return httpRequest<TokenResponseDto>("/auth/login", {
    method: "POST",
    body: credentials,
  });
}

export function fetchCurrentUser(accessToken: string): Promise<UserDto> {
  return httpRequest<UserDto>("/me", { accessToken });
}
