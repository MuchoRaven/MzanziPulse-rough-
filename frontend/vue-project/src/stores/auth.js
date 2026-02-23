import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const API_URL = 'http://localhost:5000/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const isAuthenticated = ref(false)
  const userRole = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // Load from localStorage on init
  const loadUserFromStorage = () => {
    const savedUser = localStorage.getItem('mzansi_user')
    const savedRole = localStorage.getItem('mzansi_role')
    
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
        isAuthenticated.value = true
        userRole.value = savedRole || 'business'
      } catch (e) {
        console.error('Error loading user from storage:', e)
        logout()
      }
    }
  }
  
  // Actions
  const login = async (email, password) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Login failed')
      }
      
      if (data.success) {
        setUser(data.user, 'business')
        return { success: true, user: data.user }
      } else {
        throw new Error(data.error || 'Login failed')
      }
      
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  const signup = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Signup failed')
      }
      
      if (data.success) {
        setUser(data.user, userData.role || 'business')
        return { success: true, user: data.user }
      } else {
        throw new Error(data.error || 'Signup failed')
      }
      
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  const setUser = (userData, role) => {
    user.value = userData
    userRole.value = role
    isAuthenticated.value = true
    
    // Persist to localStorage
    localStorage.setItem('mzansi_user', JSON.stringify(userData))
    localStorage.setItem('mzansi_role', role)
  }
  
  const logout = () => {
    user.value = null
    userRole.value = null
    isAuthenticated.value = false
    error.value = null
    
    // Clear localStorage
    localStorage.removeItem('mzansi_user')
    localStorage.removeItem('mzansi_role')
    
    console.log('Logged out successfully')
  }
  
  // Computed
  const isBusiness = computed(() => userRole.value === 'business')
  const isCustomer = computed(() => userRole.value === 'customer')
  
  // Initialize
  loadUserFromStorage()
  
  return {
    // State
    user,
    isAuthenticated,
    userRole,
    loading,
    error,
    
    // Computed
    isBusiness,
    isCustomer,
    
    // Actions
    login,
    signup,
    logout,
    setUser
  }
})