import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LoginCredentials } from '@/types'
import AuthService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // State
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = ref(AuthService.isAuthenticated())

  // Actions
  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null
    
    try {
      const tokens = await AuthService.login(credentials)
      isAuthenticated.value = true
      return tokens
    } catch (err: any) {
      error.value = err.response?.data?.message || '登入失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    
    try {
      await AuthService.logout()
      isAuthenticated.value = false
    } catch (err: any) {
      console.error('Logout error:', err)
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  // 初始化時檢查認證狀態
  function initialize() {
    const authenticated = AuthService.isAuthenticated()
    isAuthenticated.value = authenticated
  }

  return {
    // State
    loading,
    error,
    isAuthenticated,
    
    // Actions
    login,
    logout,
    clearError,
    initialize
  }
})
