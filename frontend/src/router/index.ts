import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/jobs'
    },
    {
      path: '/jobs',
      name: 'jobs',
      component: () => import('../views/JobListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/jobs/create',
      name: 'createJob',
      component: () => import('../views/JobCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/jobs/:id',
      name: 'jobDetail',
      component: () => import('../views/JobDetailView.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/jobs/:id/edit',
      name: 'editJob',
      component: () => import('../views/JobEditView.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      redirect: '/jobs'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
