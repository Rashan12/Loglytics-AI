export interface User {
  id: string
  email: string
  full_name: string
  subscription_tier: "free" | "pro" | "enterprise"
  selected_llm_model: "local" | "openai" | "anthropic" | "maverick"
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RegisterRequest {
  full_name: string
  email: string
  password: string
  confirm_password: string
  terms_accepted: boolean
}

export interface RegisterResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ForgotPasswordResponse {
  message: string
}

export interface ResetPasswordRequest {
  token: string
  password: string
  confirm_password: string
}

export interface ResetPasswordResponse {
  message: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthError {
  detail: string
  field?: string
  code?: string
}

export interface PasswordStrength {
  score: number
  feedback: string
  requirements: {
    length: boolean
    uppercase: boolean
    lowercase: boolean
    number: boolean
    special: boolean
  }
}

export interface SocialProvider {
  name: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

export interface FormFieldError {
  field: string
  message: string
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface AuthActions {
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (data: ResetPasswordRequest) => Promise<void>
  refreshAuth: () => Promise<void>
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}
