<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.login(email.value, password.value)
    
    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary via-primary-light to-accent flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-white rounded-xl mb-4">
          <span class="text-3xl font-bold text-primary">M</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Welcome Back!</h1>
        <p class="text-white/80">Sign in to continue growing your business</p>
      </div>

      <div class="bg-white rounded-2xl shadow-2xl p-6 lg:p-8">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Email Address
            </label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="your@email.com"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Password
            </label>
            <input
              v-model="password"
              type="password"
              required
              placeholder="••••••••"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition-all disabled:bg-neutral-300"
          >
            <span v-if="!loading">Sign In</span>
            <span v-else>Signing in...</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-neutral-600">
            Don't have an account?
            <button 
              @click="router.push('/welcome')"
              class="text-primary font-semibold hover:text-primary-dark"
            >
              Sign Up
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>