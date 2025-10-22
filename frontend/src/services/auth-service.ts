import { api } from '@/lib/api'
import { User, AuthResponse } from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await api.post('/auth/login', {
      email: email,
      password: password,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    const { access_token, token_type, user } = response.data
    localStorage.setItem('access_token', access_token)
    
    return { access_token, token_type, user }
  },

  async register(userData: {
    email: string
    full_name?: string  // CHANGED: removed username
    password: string
  }): Promise<AuthResponse> {
    const response = await api.post('/auth/register', userData)
    
    const { access_token, token_type, user } = response.data
    localStorage.setItem('access_token', access_token)
    
    return { access_token, token_type, user }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me')
    return response.data
  },

  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    const response = await api.post('/auth/refresh')
    const { access_token, token_type } = response.data
    localStorage.setItem('access_token', access_token)
    return { access_token, token_type }
  },

  logout(): void {
    localStorage.removeItem('access_token')
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }
}