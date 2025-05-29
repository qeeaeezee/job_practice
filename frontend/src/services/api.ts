import axios from 'axios'
import AuthService from './authService'

// 建立 axios 實例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 用於追蹤是否正在進行令牌刷新
let isRefreshing = false
// 待重發請求的隊列
let failedQueue: {
  resolve: (value: unknown) => void
  reject: (reason?: any) => void
  config: any
}[] = []

// 處理令牌刷新後的請求隊列
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else if (token) {
      prom.config.headers.Authorization = `Bearer ${token}`
      prom.resolve(axios(prom.config))
    }
  })
  
  // 清空隊列
  failedQueue = []
}

// 請求攔截器 - 添加 JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 響應攔截器 - 處理認證錯誤和令牌刷新
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // 如果是 401 錯誤且不是刷新令牌請求
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !originalRequest.url.includes('/auth/refresh')) {
      
      if (isRefreshing) {
        // 如果已經在刷新中，將請求加入隊列
        try {
          const token = await new Promise((resolve, reject) => {
            failedQueue.push({
              resolve,
              reject,
              config: originalRequest
            })
          })
          return token
        } catch (err) {
          return Promise.reject(err)
        }
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        // 嘗試刷新令牌
        const tokens = await AuthService.refreshToken()
        
        // 更新請求頭
        const newToken = tokens.access
        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
        
        // 重新發送之前的請求
        processQueue(null, newToken)
        
        // 返回帶有新令牌的重試請求
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return axios(originalRequest)
      } catch (refreshError) {
        // 刷新令牌失敗，清除所有令牌並重定向到登入頁
        processQueue(refreshError, null)
        
        // 清除本地存儲
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // 這裡可以添加重定向邏輯或讓路由守衛處理
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
