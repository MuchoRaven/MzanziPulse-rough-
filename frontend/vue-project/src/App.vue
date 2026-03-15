<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const { t } = useI18n()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Check if current route needs blank layout (no nav/sidebar)
const isBlankLayout = computed(() => {
  return route.meta?.layout === 'blank' || !authStore.isAuthenticated
})

const navItems = computed(() => [
  { name: t('nav.dashboard'), path: '/', icon: '📊', description: t('nav.overview') },
  { name: t('nav.bizBantu'), path: '/biz-bantu', icon: '🤖', description: t('nav.aiAssistant') },
  { name: t('nav.bizSeed'), path: '/biz-seed', icon: '🌱', description: t('nav.grantsFunding') },
  { name: t('nav.wallet'), path: '/wallet', icon: '💰', description: t('nav.cashTracking') }
])

const isActive = (path) => route.path === path

const navigateTo = (path) => {
  router.push(path)
}

const handleLogout = () => {
  if (confirm('Are you sure you want to sign out?')) {
    authStore.logout()
    router.push('/welcome')
  }
}

const getUserInitial = () => {
  if (authStore.user?.firstName) {
    return authStore.user.firstName[0].toUpperCase()
  }
  return 'U'
}

const getDisplayName = () => {
  if (authStore.user?.firstName && authStore.user?.lastName) {
    return `${authStore.user.firstName} ${authStore.user.lastName}`
  }
  return 'User'
}

const getBusinessName = () => {
  if (authStore.user?.businessName) {
    return authStore.user.businessName
  }
  return "Your Business"
}
</script>

<template>
  <!-- BLANK LAYOUT (Auth pages - no navigation) -->
  <div v-if="isBlankLayout" class="min-h-screen">
    <RouterView />
  </div>

  <!-- APP LAYOUT (Protected pages - with navigation) -->
  <div v-else class="min-h-screen bg-neutral-50">
    <!-- Desktop Sidebar -->
    <aside class="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-64 bg-white border-r border-neutral-200 z-30">
      <div class="flex items-center gap-3 px-6 py-5 border-b border-neutral-200">
        <div class="w-10 h-10 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center text-white text-xl font-bold">
          M
        </div>
        <div>
          <h1 class="text-lg font-bold text-neutral-900">MzansiPulse</h1>
          <p class="text-xs text-neutral-500">Biz Growth Hub</p>
        </div>
      </div>

      <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto scrollbar-hide">
        <button
          v-for="item in navItems"
          :key="item.path"
          @click="navigateTo(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
            isActive(item.path)
              ? 'bg-primary text-white shadow-md'
              : 'text-neutral-700 hover:bg-neutral-100'
          ]"
        >
          <span class="text-2xl">{{ item.icon }}</span>
          <div class="flex-1 text-left">
            <p class="font-medium">{{ item.name }}</p>
            <p :class="[
              'text-xs',
              isActive(item.path) ? 'text-orange-100' : 'text-neutral-500'
            ]">
              {{ item.description }}
            </p>
          </div>
        </button>
      </nav>

      <div class="px-4 py-4 border-t border-neutral-200">
        <div class="px-4 py-3 rounded-lg bg-neutral-50">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-success rounded-full flex items-center justify-center text-white font-bold">
              {{ getUserInitial() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-neutral-900 truncate">
                {{ getDisplayName() }}
              </p>
              <p class="text-xs text-neutral-500 truncate">
                {{ getBusinessName() }}
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between mb-2">
            <LanguageSwitcher />
          </div>
          <button
            @click="handleLogout"
            class="w-full py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
          >
            <span>🚪</span>
            <span>{{ t('nav.signOut') }}</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Mobile Header -->
    <header class="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-neutral-200 z-20">
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center text-white text-sm font-bold">
            M
          </div>
          <h1 class="text-lg font-bold text-neutral-900">MzansiPulse</h1>
        </div>
        
        <div class="flex items-center gap-2">
          <LanguageSwitcher />
          <button
            @click="handleLogout"
            class="w-8 h-8 bg-success rounded-full flex items-center justify-center text-white text-sm font-bold hover:opacity-80 transition-opacity"
            :title="t('nav.signOut')"
          >
            {{ getUserInitial() }}
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main :class="[
      'min-h-screen transition-all',
      'lg:ml-64',
      'pt-14 pb-20 lg:pt-0 lg:pb-0'
    ]">
      <div class="max-w-7xl mx-auto px-4 py-6 lg:px-8 lg:py-8">
        <RouterView />
      </div>
    </main>

    <!-- Bottom Navigation (Mobile) -->
    <nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 z-20">
      <div class="flex justify-around items-center px-2 py-2">
        <button
          v-for="item in navItems"
          :key="item.path"
          @click="navigateTo(item.path)"
          :class="[
            'flex flex-col items-center justify-center flex-1 py-2 px-1 rounded-lg transition-all min-h-touch',
            isActive(item.path) ? 'text-primary' : 'text-neutral-500'
          ]"
        >
          <span class="text-2xl mb-1">{{ item.icon }}</span>
          <span class="text-xs font-medium">{{ item.name }}</span>
        </button>
      </div>
    </nav>
  </div>
</template>