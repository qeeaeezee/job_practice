<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(() => {
  authStore.initialize()
})

const toggleLanguage = () => {
  locale.value = locale.value === 'zh-TW' ? 'en' : 'zh-TW'
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app">
    <header v-if="isAuthenticated" class="header">
      <div class="container">
        <div class="header-content">
          <h1 class="logo">{{ t('app.title') }}</h1>
          
          <nav class="nav">
            <router-link to="/jobs" class="nav-link">
              {{ t('navigation.jobs') }}
            </router-link>
            <router-link to="/jobs/create" class="nav-link">
              {{ t('navigation.createJob') }}
            </router-link>
          </nav>

          <div class="header-actions">
            <button @click="toggleLanguage" class="btn btn-secondary">
              {{ locale === 'zh-TW' ? 'EN' : '中文' }}
            </button>
            
            <div class="user-info">
              <span>{{ t('common.welcome') }}</span>
              <button @click="logout" class="btn btn-outline">
                {{ t('auth.logout') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <header v-else class="header">
      <div class="container">
        <div class="header-content">
          <h1 class="logo">{{ t('app.title') }}</h1>
          
          <div class="header-actions">
            <button @click="toggleLanguage" class="btn btn-secondary">
              {{ locale === 'zh-TW' ? 'EN' : '中文' }}
            </button>
            
            <div class="user-info">
              <router-link to="/login" class="btn btn-primary">
                {{ t('auth.login') }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.header {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 0 1rem; /* Add padding for smaller screens */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  /* padding: 0 1rem; Remove padding here, apply to header and main directly */
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4.5rem;
  width: 100%; /* Ensure full width */
}

.logo {
  font-size: 1.6rem;
  font-weight: bold;
  color: #2563eb;
  margin: 0;
  letter-spacing: -0.5px;
  transition: color 0.3s;
}

.logo:hover {
  color: #1d4ed8;
}

.nav {
  display: flex;
  gap: 1rem; /* Reduce gap for smaller screens */
}

.nav-link {
  color: #4b5563;
  text-decoration: none;
  font-weight: 500;
  font-size: 1.05rem;
  transition: all 0.2s;
  position: relative;
  padding: 0.5rem 0;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.nav-link:hover {
  color: #1f2937;
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.nav-link.router-link-active {
  color: #1f2937;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem; /* Reduce gap */
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.user-info span {
  font-weight: 500;
  color: #374151;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  font-size: 0.95rem;
}

.btn-secondary {
  background-color: #4f46e5;
  color: white;
}

.btn-secondary:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.25);
}

.btn-primary {
  background-color: #2563eb;
  color: white;
  border: none;
  text-decoration: none;
}

.btn-primary:hover {
  background-color: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
}

.btn-outline {
  background-color: transparent;
  color: #4b5563;
  border: 1px solid #d1d5db;
  text-decoration: none;
}

.btn-outline:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
  color: #1f2937;
}

.main {
  min-height: calc(100vh - 4.5rem); /* Adjust based on header height */
  padding: 1.5rem 1rem; /* Add padding for smaller screens */
  background-color: #f8fafc;
}

/* Tablet and larger screens */
@media (min-width: 769px) {
  .header {
    padding: 0 2rem; /* Larger padding for larger screens */
  }

  .nav {
    gap: 2.5rem; /* Restore larger gap */
  }

  .header-actions {
    gap: 1.25rem; /* Restore larger gap */
  }
  
  .main {
    padding: 2rem; /* Larger padding for larger screens */
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 1rem 0;
    gap: 1rem; /* Adjust gap for stacked items */
  }

  .logo {
    margin-bottom: 0.5rem; /* Add some space below logo when stacked */
  }

  .nav {
    order: 1; /* Ensure nav comes after logo if needed, or adjust as per design */
    gap: 1rem; /* Further adjust gap for mobile nav */
    overflow-x: auto;
    padding: 0.5rem 0;
    width: 100%;
    justify-content: center;
    border-top: 1px solid #e5e7eb; /* Optional: separator for stacked nav */
    border-bottom: 1px solid #e5e7eb; /* Optional: separator for stacked nav */
    margin-top: 0.5rem;
  }

  .nav-link {
    font-size: 1rem; /* Slightly smaller font for mobile nav */
    padding: 0.5rem 0.75rem; /* Adjust padding for touch targets */
  }
  
  .nav-link::after {
    /* Optionally disable or modify underline for mobile */
    height: 0; 
  }

  .nav-link.router-link-active {
    /* Mobile active link style */
    color: #2563eb;
    font-weight: bold;
  }


  .header-actions {
    order: 2; /* Ensure actions come after nav if needed */
    width: 100%;
    justify-content: space-around; /* Distribute items like language and login */
    margin-top: 0.5rem;
  }

  .user-info {
    flex-direction: column; /* Stack user info items */
    text-align: center;
    gap: 0.5rem; /* Reduce gap in stacked user info */
    padding: 0.5rem; /* Adjust padding */
    width: 100%; /* Make user info take full width if needed */
  }
  
  .user-info span {
    margin-bottom: 0.5rem; /* Space between welcome text and logout button */
  }

  .btn {
    width: auto; /* Allow buttons to size based on content or be full width */
    padding: 0.75rem 1rem; /* Adjust button padding for touch */
  }
  
  .main {
    padding: 1rem; /* Adjust main content padding for mobile */
  }
}
</style>
