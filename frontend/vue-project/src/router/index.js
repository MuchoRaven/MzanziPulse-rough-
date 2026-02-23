import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public routes
    {
      path: '/welcome',
      name: 'welcome',
      component: () => import('../views/Landing.vue'),
      meta: { requiresGuest: true, layout: 'blank' }
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/Signup.vue'),
      meta: { requiresGuest: true, layout: 'blank' }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: { requiresGuest: true, layout: 'blank' }
    },
    {
      path: '/customer-coming-soon',
      name: 'customer-coming-soon',
      component: () => import('../views/CustomerComingSoon.vue'),
      meta: { layout: 'blank' }
    },
    
    // Protected routes (require auth)
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/biz-bantu',
      name: 'biz-bantu',
      component: () => import('../views/BizBantu.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/biz-seed',
      name: 'biz-seed',
      component: () => import('../views/BizSeed.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/wallet',
      name: 'wallet',
      component: () => import('../views/Wallet.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Redirect root to welcome if not authenticated
  if (to.path === '/' && !authStore.isAuthenticated) {
    next('/welcome')
    return
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/welcome')
    return
  }
  
  // Check if route requires guest (not logged in)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

export default router