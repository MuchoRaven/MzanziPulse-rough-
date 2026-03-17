<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- Header with Add Transaction Button -->
    <div class="bg-white border-b border-neutral-200 px-4 py-4 lg:px-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">{{ greeting }}</h1>
          <p class="text-neutral-500 text-sm">{{ userData.businessName }} • {{ userData.location }}</p>
        </div>
        
        <!-- Add Transaction Button -->
        <button
          @click="showAddTransaction = true"
          class="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors shadow-md"
        >
          <span class="text-xl">📷</span>
          <span>{{ $t('dashboard.addTransaction') }}</span>
        </button>
      </div>
    </div>

    <div class="p-4 lg:p-6 space-y-6">
      <!-- Wallet Balance Card -->
      <div class="bg-gradient-to-br from-primary to-primary-dark text-white rounded-2xl p-6 shadow-lg">
        <p class="text-primary-100 text-sm mb-1">{{ $t('dashboard.totalBalance') }}</p>
        <h2 class="text-4xl font-bold mb-4">R{{ walletBalance.toFixed(2) }}</h2>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-primary-100">{{ $t('dashboard.cashBalance') }}</p>
            <p class="text-xl font-semibold">R{{ cashBalance.toFixed(2) }}</p>
          </div>
          <div>
            <p class="text-primary-100">{{ $t('dashboard.digitalBalance') }}</p>
            <p class="text-xl font-semibold">R{{ digitalBalance.toFixed(2) }}</p>
          </div>
        </div>
      </div>

      <!-- EmpowerScore Card -->
      <EmpowerScoreCard
        :score="userData.score"
        :tier="userData.tier"
        :balance="userData.balance"
        :cash-balance="userData.cashBalance"
        :digital-balance="userData.digitalBalance"
      />

      <!-- Quick Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl p-4 shadow-md">
          <p class="text-neutral-500 text-sm">{{ $t('dashboard.dailySales') }}</p>
          <p class="text-2xl font-bold text-neutral-900">R{{ dailySales.toFixed(0) }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-md">
          <p class="text-neutral-500 text-sm">{{ $t('dashboard.monthlyProfit') }}</p>
          <p class="text-2xl font-bold text-success">R{{ monthlyProfit.toFixed(0) }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-md">
          <p class="text-neutral-500 text-sm">{{ $t('dashboard.transactions') }}</p>
          <p class="text-2xl font-bold text-neutral-900">{{ transactionCount }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-md">
          <p class="text-neutral-500 text-sm">{{ $t('dashboard.empowerScore') }}</p>
          <p class="text-2xl font-bold text-primary">{{ empowerScore }}</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <section>
        <h2 class="text-lg font-semibold text-neutral-900 mb-4">{{ $t('dashboard.quickActions') }}</h2>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
          <QuickActionCard
            v-for="action in quickActions"
            :key="action.title"
            :title="action.title"
            :description="action.description"
            :icon="action.icon"
            :color="action.color"
            @click="action.action"
          />
        </div>
      </section>

      <!-- Transactions List -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <span></span>
          <router-link
            to="/ledger"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-medium hover:bg-primary-dark transition-colors"
          >📖 Full Ledger</router-link>
        </div>
        <TransactionsList
          ref="transactionsListRef"
          @add-transaction="showAddTransaction = true"
        />
      </div>

      <!-- Grants Carousel -->
      <section>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-neutral-900">🌱 {{ $t('dashboard.grantsTitle') }}</h2>
          <router-link
            to="/biz-seed"
            class="text-sm font-medium text-success hover:text-success-dark transition-colors"
          >{{ $t('dashboard.seeAll') }} →</router-link>
        </div>

        <!-- Loaded grants -->
        <div
          v-if="eligibleGrants.length"
          class="lg:grid lg:grid-cols-3 lg:gap-4 flex lg:flex-none gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-4 px-4 lg:mx-0 lg:px-0"
        >
          <GrantCard
            v-for="grant in eligibleGrants"
            :key="grant.id"
            :grant="grant"
            class="flex-shrink-0 w-80 lg:w-auto"
          />
        </div>

        <!-- No eligible grants yet -->
        <div v-else class="bg-white rounded-xl border border-neutral-200 p-6 text-center">
          <span class="text-4xl block mb-2">🔍</span>
          <p class="text-neutral-600 font-medium text-sm">No grants matched to your profile yet</p>
          <p class="text-xs text-neutral-400 mt-1">Complete your business profile in Biz-Seed to unlock funding matches.</p>
        </div>
      </section>

      <!-- Tips Section -->
      <section class="bg-gradient-to-br from-primary-light/10 to-accent/10 rounded-xl p-6 border border-primary/20">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl flex-shrink-0">
            💡
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-neutral-900 mb-2">{{ $t('dashboard.tipTitle') }}</h3>
            <p class="text-sm text-neutral-700 leading-relaxed">
              Your consistency score is great (83%)! To reach PRIME tier, 
              try adding 2-3 new product lines. This will improve your 
              diversity score by 15-20 points. 🚀
            </p>
          </div>
        </div>
      </section>
    </div>

    <!-- Add Transaction Modal -->
    <AddTransactionModal
      :is-open="showAddTransaction"
      @close="showAddTransaction = false"
      @success="handleTransactionAdded"
    />
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import EmpowerScoreCard from '../components/EmpowerScoreCard.vue'
import QuickActionCard from '../components/QuickActionCard.vue'
import GrantCard from '../components/GrantCard.vue'
import TransactionsList from '../components/TransactionsList.vue'
import AddTransactionModal from '../components/AddTransactionModal.vue'

const authStore = useAuthStore()

const showAddTransaction  = ref(false)
const transactionsListRef = ref(null)

// Wallet data
const walletBalance = ref(0)
const cashBalance = ref(0)
const digitalBalance = ref(0)
const dailySales = ref(0)
const monthlyProfit = ref(0)
const transactionCount = ref(0)
const empowerScore = ref(0)
const empowerTier = ref('DEVELOPING')
const empowerBreakdown = ref({})

const fetchDashboardData = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard/${authStore.user?.id}`)
    const data = await response.json()

    if (data.success) {
      // Use Number() to guarantee JS numbers even if backend sends Decimal strings
      walletBalance.value   = Number(data.wallet?.totalBalance)   || 0
      cashBalance.value     = Number(data.wallet?.cashBalance)     || 0
      digitalBalance.value  = Number(data.wallet?.digitalBalance)  || 0

      dailySales.value      = Number(data.analytics?.averageDailySales) || 0
      monthlyProfit.value   = Number(data.analytics?.profit)            || 0
      transactionCount.value = Number(data.analytics?.transactionCount) || 0
      empowerScore.value    = Number(data.empowerScore)  || 0
      empowerTier.value     = data.empowerTier           || 'DEVELOPING'
      empowerBreakdown.value = data.empowerBreakdown     || {}
      
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

const handleTransactionAdded = () => {
  // Refresh transactions list
  if (transactionsListRef.value) {
    transactionsListRef.value.refreshTransactions()
  }
  
  // Refresh dashboard data
  fetchDashboardData()
}

onMounted(() => {
  fetchDashboardData()
  fetchEligibleGrants()
})

// Get real user data from auth store (with fallbacks for demo)
const userData = computed(() => ({
  name: authStore.user?.firstName || 'Entrepreneur',
  businessName: authStore.user?.businessName || "Your Business",
  location: authStore.user?.location || 'South Africa',
  score: empowerScore.value,
  tier: empowerTier.value,
  balance: walletBalance.value,
  cashBalance: cashBalance.value,
  digitalBalance: digitalBalance.value
}))

// TIME-BASED GREETING
const greeting = computed(() => {
  const hour = new Date().getHours()
  const name = userData.value.name
  
  if (hour >= 5 && hour < 12) {
    return `Good morning, ${name}! ☀️`
  } else if (hour >= 12 && hour < 17) {
    return `Good afternoon, ${name}! 🌤️`
  } else if (hour >= 17 && hour < 23) {
    return `Good evening, ${name}! 🌆`
  } else {
    return `Good night, ${name}! 🌙`
  }
})

// Quick actions (computed so labels update on locale change)
const quickActions = computed(() => [
  {
    title: t('dashboard.addTransaction'),
    description: t('transactions.add'),
    icon: '➕',
    color: 'primary',
    action: () => { showAddTransaction.value = true }
  },
  {
    title: t('nav.bizBantu'),
    description: t('nav.aiAssistant'),
    icon: '🤖',
    color: 'success',
    action: () => { window.location.href = '/biz-bantu' }
  },
  {
    title: t('nav.bizSeed'),
    description: t('nav.grantsFunding'),
    icon: '🌱',
    color: 'accent',
    action: () => { window.location.href = '/biz-seed' }
  },
  {
    title: 'Transaction Ledger',
    description: 'Bank statement view',
    icon: '📖',
    color: 'neutral',
    action: () => { window.location.href = '/ledger' }
  }
])

// Top 3 eligible grants — fetched live from the grant matcher
const eligibleGrants = ref([])

const fetchEligibleGrants = async () => {
  try {
    const res  = await fetch(`${API_BASE}/api/bizseed/grants/matches/${authStore.user?.id}`)
    const data = await res.json()
    if (data.success) {
      // Only show grants the user actually qualifies for, top 3 by match %
      eligibleGrants.value = data.grants
        .filter(g => g.eligible)
        .sort((a, b) => b.match - a.match)
        .slice(0, 3)
    }
  } catch (e) {
    console.error('Failed to fetch grants:', e)
  }
}
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>