import api from './api'
import type { AuthTokens, LoginCredentials, TokenRefreshRequest } from '@/types'

export class AuthService {
  static async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await api.post('/auth/login', credentials)
    const tokens = response.data
    
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
    
    return tokens
  }

  static async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await api.post('/auth/logout', { refresh: refreshToken })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  static async refreshToken(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }
    
    const payload: TokenRefreshRequest = { refresh: refreshToken }
    const response = await api.post('/auth/refresh', payload)
    const tokens = response.data
    
    localStorage.setItem('access_token', tokens.access)
    if (tokens.refresh) {
      localStorage.setItem('refresh_token', tokens.refresh)
    }
    
    return tokens
  }

  static isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  static getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }
}

export default AuthService
