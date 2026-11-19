// packages/api-types/src/index.ts

export type UserRole = "admin" | "sales" | "hr" | "finance";

export interface UserDto {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  domain: string;
  is_superuser: boolean;
}

export interface LoginRequestDto {
  username: string;
  password: string;
}

export interface TokenResponseDto {
  access: string;
  refresh: string;
}

export interface RefreshRequestDto {
  refresh: string;
}

export interface InvoiceListResponseDto {
  domain: string;
  invoices: Array<Record<string, unknown>>;
}
