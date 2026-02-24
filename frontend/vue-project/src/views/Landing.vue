<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const chooseRole = (role) => {
  if (role === 'customer') {
    router.push('/customer-coming-soon')
  } else {
    router.push('/signup')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary via-primary-light to-accent flex items-center justify-center p-4">
    <div class="max-w-4xl w-full">
      <!-- Logo & Tagline -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-white rounded-2xl shadow-2xl mb-6">
          <span class="text-4xl font-bold text-primary">M</span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold text-white mb-3">
          Welcome to MzansiPulse
        </h1>
        <p class="text-lg lg:text-xl text-white/90 max-w-2xl mx-auto">
          Your AI-powered business growth companion for South Africa's township economy
        </p>
      </div>

      <!-- Role Selection Cards -->
      <div class="grid grid-cols-2 gap-4 lg:gap-8">
        <!-- Business Owner Card -->
        <button
          @click="chooseRole('business')"
          class="bg-white rounded-2xl p-8 lg:p-10 text-left shadow-2xl hover:shadow-3xl transition-all hover:scale-105 active:scale-100 group"
        >
          <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary/20 transition-colors">
            <span class="text-4xl">👔</span>
          </div>
          
          <h2 class="text-lg lg:text-2xl xl:text-3xl font-bold text-neutral-900 mb-2 lg:mb-3">
           I'm a Business Owner
          </h2>

          <p class="text-xs lg:text-base text-neutral-600 mb-4 lg:mb-6 leading-relaxed">
            Run a spaza shop, salon, tailor, or any township business? 
            Get your EmpowerScore, track cash, and find grants.
          </p>
          
          <div class="flex items-center gap-2 text-primary font-semibold group-hover:gap-3 transition-all">
            <span>Start Growing</span>
            <span class="text-xl">→</span>
          </div>
        </button>

        <!-- Customer Card -->
        <button
          @click="chooseRole('customer')"
          class="bg-white rounded-2xl p-8 lg:p-10 text-left shadow-2xl hover:shadow-3xl transition-all hover:scale-105 active:scale-100 group"
        >
          <div class="w-16 h-16 bg-success/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-success/20 transition-colors">
            <span class="text-4xl">🛒</span>
          </div>
          
          <h2 class="text-lg lg:text-2xl xl:text-3xl font-bold text-neutral-900 mb-2 lg:mb-3">
            I'm a Customer
          </h2>

          <p class="text-xs lg:text-base text-neutral-600 mb-4 lg:mb-6 leading-relaxed">
            Support local businesses, discover township shops, and enjoy 
            community-powered shopping experiences.
          </p>
          
          <div class="flex items-center gap-2 text-success font-semibold group-hover:gap-3 transition-all">
            <span>Explore Shops</span>
            <span class="text-xl">→</span>
          </div>
        </button>
      </div>

      <!-- Login Link -->
      <div class="text-center mt-8">
        <p class="text-white/80">
          Already have an account?
          <button 
            @click="router.push('/login')"
            class="font-semibold text-white hover:text-white/90 underline ml-2"
          >
            Sign In
          </button>
        </p>
      </div>
    </div>
  </div>
</template>