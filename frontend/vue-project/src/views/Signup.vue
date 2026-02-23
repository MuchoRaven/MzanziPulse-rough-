<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const currentStep = ref(1)
const loading = ref(false)
const error = ref('')

// Form data
const formData = ref({
  // Step 1: Personal Info
  firstName: '',
  lastName: '',
  phone: '',
  
  // Step 2: Business Info
  businessName: '',
  businessType: '',
  location: '',
  
  // Step 3: Account Setup
  email: '',
  password: '',
  confirmPassword: ''
})

// Business type options
const businessTypes = [
  { value: 'SPAZA_SHOP', label: '🏪 Spaza Shop', description: 'Convenience store' },
  { value: 'SALON', label: '💇 Hair Salon', description: 'Beauty services' },
  { value: 'TAILOR', label: '🪡 Tailor Shop', description: 'Sewing & alterations' },
  { value: 'RESTAURANT', label: '🍲 Restaurant/Takeaway', description: 'Food services' },
  { value: 'MECHANIC', label: '🔧 Mechanic', description: 'Auto repairs' },
  { value: 'OTHER', label: '📦 Other Business', description: 'Something else' }
]

// Validation
const canProceedStep1 = computed(() => {
  return formData.value.firstName.trim() && 
         formData.value.lastName.trim() && 
         formData.value.phone.length >= 10
})

const canProceedStep2 = computed(() => {
  return formData.value.businessName.trim() && 
         formData.value.businessType && 
         formData.value.location.trim()
})

const canSubmit = computed(() => {
  return formData.value.email.includes('@') && 
         formData.value.password.length >= 6 && 
         formData.value.password === formData.value.confirmPassword
})

// Actions
const nextStep = () => {
  error.value = ''
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  error.value = ''
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const submitSignup = async () => {
  if (!canSubmit.value) {
    error.value = 'Please fill in all required fields correctly'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.signup({
      ...formData.value,
      role: 'business'
    })
    
    if (result.success) {
      // Success! Redirect to dashboard
      router.push('/')
    } else {
      error.value = result.error || 'Signup failed. Please try again.'
    }
  } catch (err) {
    error.value = 'Something went wrong. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
    <div class="max-w-2xl w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <button 
          @click="router.push('/welcome')"
          class="inline-flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-4"
        >
          <span>←</span>
          <span>Back</span>
        </button>
        
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-xl mb-4">
          <span class="text-3xl font-bold text-white">M</span>
        </div>
        
        <h1 class="text-3xl font-bold text-neutral-900 mb-2">
          Create Your Business Account
        </h1>
        <p class="text-neutral-600">
          Step {{ currentStep }} of 3
        </p>
      </div>

      <!-- Progress Bar -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-2">
          <span :class="['text-sm font-medium', currentStep >= 1 ? 'text-primary' : 'text-neutral-400']">
            Personal
          </span>
          <span :class="['text-sm font-medium', currentStep >= 2 ? 'text-primary' : 'text-neutral-400']">
            Business
          </span>
          <span :class="['text-sm font-medium', currentStep >= 3 ? 'text-primary' : 'text-neutral-400']">
            Account
          </span>
        </div>
        <div class="h-2 bg-neutral-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-primary transition-all duration-300"
            :style="{ width: `${(currentStep / 3) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Form Card -->
      <div class="bg-white rounded-2xl shadow-lg p-6 lg:p-8">
        <!-- Step 1: Personal Info -->
        <div v-show="currentStep === 1" class="space-y-4 animate-fade-in">
          <h2 class="text-xl font-bold text-neutral-900 mb-4">
            👤 Tell us about yourself
          </h2>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              First Name *
            </label>
            <input
              v-model="formData.firstName"
              type="text"
              placeholder="Thandi"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Last Name *
            </label>
            <input
              v-model="formData.lastName"
              type="text"
              placeholder="Molefe"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Phone Number *
            </label>
            <input
              v-model="formData.phone"
              type="tel"
              placeholder="0821234567"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
            <p class="text-xs text-neutral-500 mt-1">
              We'll use this for WhatsApp transaction logging
            </p>
          </div>

          <button
            @click="nextStep"
            :disabled="!canProceedStep1"
            :class="[
              'w-full py-3 rounded-lg font-semibold transition-all mt-6',
              canProceedStep1
                ? 'bg-primary text-white hover:bg-primary-dark'
                : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
            ]"
          >
            Continue →
          </button>
        </div>

        <!-- Step 2: Business Info -->
        <div v-show="currentStep === 2" class="space-y-4 animate-fade-in">
          <h2 class="text-xl font-bold text-neutral-900 mb-4">
            🏪 Tell us about your business
          </h2>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Business Name *
            </label>
            <input
              v-model="formData.businessName"
              type="text"
              placeholder="Mama Thandi's Spaza Shop"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Business Type *
            </label>
            <div class="grid grid-cols-2 gap-3">
              <button
                v-for="type in businessTypes"
                :key="type.value"
                @click="formData.businessType = type.value"
                :class="[
                  'p-3 rounded-lg border-2 text-left transition-all',
                  formData.businessType === type.value
                    ? 'border-primary bg-primary/5'
                    : 'border-neutral-200 hover:border-neutral-300'
                ]"
              >
                <div class="font-semibold text-sm">{{ type.label }}</div>
                <div class="text-xs text-neutral-500">{{ type.description }}</div>
              </button>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Location (Township/Area) *
            </label>
            <input
              v-model="formData.location"
              type="text"
              placeholder="Soweto, Gauteng"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>

          <div class="flex gap-3 mt-6">
            <button
              @click="prevStep"
              class="flex-1 py-3 rounded-lg font-semibold border-2 border-neutral-300 text-neutral-700 hover:bg-neutral-50 transition-all"
            >
              ← Back
            </button>
            <button
              @click="nextStep"
              :disabled="!canProceedStep2"
              :class="[
                'flex-1 py-3 rounded-lg font-semibold transition-all',
                canProceedStep2
                  ? 'bg-primary text-white hover:bg-primary-dark'
                  : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
              ]"
            >
              Continue →
            </button>
          </div>
        </div>

        <!-- Step 3: Account Setup -->
        <div v-show="currentStep === 3" class="space-y-4 animate-fade-in">
          <h2 class="text-xl font-bold text-neutral-900 mb-4">
            🔐 Secure your account
          </h2>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Email Address *
            </label>
            <input
              v-model="formData.email"
              type="email"
              placeholder="thandi@example.com"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Password *
            </label>
            <input
              v-model="formData.password"
              type="password"
              placeholder="Min. 6 characters"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-neutral-700 mb-2">
              Confirm Password *
            </label>
            <input
              v-model="formData.confirmPassword"
              type="password"
              placeholder="Re-enter password"
              :class="[
                'w-full px-4 py-3 rounded-lg border outline-none transition-all',
                formData.confirmPassword && formData.password !== formData.confirmPassword
                  ? 'border-red-500 focus:ring-red-200'
                  : 'border-neutral-300 focus:border-primary focus:ring-primary/20'
              ]"
            />
            <p v-if="formData.confirmPassword && formData.password !== formData.confirmPassword" class="text-xs text-red-600 mt-1">
              Passwords don't match
            </p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <div class="flex gap-3 mt-6">
            <button
              @click="prevStep"
              class="flex-1 py-3 rounded-lg font-semibold border-2 border-neutral-300 text-neutral-700 hover:bg-neutral-50 transition-all"
            >
              ← Back
            </button>
            <button
              @click="submitSignup"
              :disabled="!canSubmit || loading"
              :class="[
                'flex-1 py-3 rounded-lg font-semibold transition-all',
                canSubmit && !loading
                  ? 'bg-success text-white hover:bg-success-dark'
                  : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
              ]"
            >
              <span v-if="!loading">Create Account ✓</span>
              <span v-else>Creating...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>