<template>
  <div class="login-view">
    <div class="login-container">
      <h1>{{ $t('auth.login') }}</h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">{{ $t('auth.username') }}</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            required
            :placeholder="$t('auth.usernamePlaceholder')"
          />
        </div>
        
        <div class="form-group">
          <label for="password">{{ $t('auth.password') }}</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            :placeholder="$t('auth.passwordPlaceholder')"
          />
        </div>
        
        <button type="submit" :disabled="isLoading" class="login-btn">
          {{ isLoading ? $t('common.loading') : $t('auth.login') }}
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const credentials = ref({
  username: '',
  password: ''
})

const error = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  try {
    error.value = ''
    isLoading.value = true
    await authStore.login(credentials.value)
    
    // 登入成功後，檢查是否有重定向路徑
    const redirectPath = route.query.redirect as string || '/jobs'
    router.push(redirectPath)
    
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || t('auth.loginFailed')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  background: #ffffff; /* 白色背景 */
  padding: 2.5rem 3rem; /* 增加內邊距 */
  border-radius: 12px; /* 更大的圓角 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); /* 更柔和的陰影 */
  width: 100%;
  max-width: 420px; /* 略微增加寬度 */
  text-align: center; /* 標題居中 */
}

.login-container h1 {
  color: #333; /* 深色標題 */
  margin-bottom: 2rem; /* 增加標題與表單間距 */
  font-size: 2rem; /* 調整標題大小 */
  font-weight: 600; /* 標題字重 */
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Increased gap between form elements */
}

.form-group {
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem; /* Spacing between label and input */
  font-weight: 500;
  color: #4a5568; /* Label color */
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem; /* Increased padding */
  border: 1px solid #cbd5e0; /* Softer border color */
  border-radius: 0.5rem; /* Rounded corners */
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4299e1; /* Blue border on focus */
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5); /* Blue shadow on focus */
}

.login-btn {
  background-color: #4299e1; /* Blue button */
  color: white;
  padding: 0.9rem; /* Increased padding */
  border: none;
  border-radius: 0.5rem; /* Rounded corners */
  cursor: pointer;
  font-size: 1.1rem; /* Larger font size */
  font-weight: 500;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 1rem; /* Added margin on top */
}

.login-btn:hover {
  background-color: #3182ce; /* Darker blue on hover */
}

.login-btn:active {
  transform: translateY(1px); /* Slight press effect */
}

.login-btn:disabled {
  background-color: #a0aec0; /* Gray when disabled */
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e; /* Red error message */
  margin-top: 1.5rem; /* Increased margin */
  font-weight: 500;
}
</style>
