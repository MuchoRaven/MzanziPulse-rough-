<template>
  <div class="min-h-screen bg-gradient-to-br from-success via-success-light to-accent/50 flex items-center justify-center p-4">
    <div class="max-w-2xl w-full text-center">
      <div class="text-8xl mb-6">🛒</div>
      <h1 class="text-4xl lg:text-5xl font-bold text-white mb-4">
        Customer Platform Coming Soon!
      </h1>
      <p class="text-xl text-white/90 mb-8 max-w-xl mx-auto">
        We're building an amazing experience for customers to discover and support local township businesses. Stay tuned!
      </p>
      
      <div class="bg-white rounded-2xl p-8 shadow-2xl">
        <h2 class="text-2xl font-bold text-neutral-900 mb-4">
          What to expect:
        </h2>
        <ul class="text-left space-y-3 mb-6">
          <li class="flex items-start gap-3">
            <span class="text-2xl">🗺️</span>
            <div>
              <p class="font-semibold text-neutral-900">Discover Local Shops</p>
              <p class="text-sm text-neutral-600">Find spaza shops, salons, and services near you</p>
            </div>
          </li>
          <li class="flex items-start gap-3">
            <span class="text-2xl">💳</span>
            <div>
              <p class="font-semibold text-neutral-900">Easy Payments</p>
              <p class="text-sm text-neutral-600">Pay with cash, card, or eWallet</p>
            </div>
          </li>
          <li class="flex items-start gap-3">
            <span class="text-2xl">🎁</span>
            <div>
              <p class="font-semibold text-neutral-900">Rewards & Loyalty</p>
              <p class="text-sm text-neutral-600">Earn points and get discounts</p>
            </div>
          </li>
        </ul>

        <button
          @click="$router.push('/welcome')"
          class="w-full py-3 bg-success text-white rounded-lg font-semibold hover:bg-success-dark transition-all"
        >
          ← Back to Home
        </button>
      </div>
    </div>
  </div>
</template>