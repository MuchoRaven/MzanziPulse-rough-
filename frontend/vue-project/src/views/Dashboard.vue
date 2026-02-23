<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import EmpowerScoreCard from '../components/EmpowerScoreCard.vue'
import QuickActionCard from '../components/QuickActionCard.vue'
import TransactionItem from '../components/TransactionItem.vue'
import GrantCard from '../components/GrantCard.vue'

const authStore = useAuthStore()

// Get real user data from auth store (with fallbacks for demo)
const userData = computed(() => ({
  name: authStore.user?.firstName || 'Thandi',
  businessName: authStore.user?.businessName || "Mama Thandi's Spaza Shop",
  location: authStore.user?.location || 'Soweto, Gauteng',
  score: 542,
  tier: 'BUILDER',
  balance: 7500.00,
  cashBalance: 7450.00,
  digitalBalance: 50.00
}))

// Simulated transactions
const recentTransactions = ref([
  {
    id: 1,
    description: '15 bread loaves sold',
    amount: 75.00,
    type: 'income',
    category: 'GROCERIES',
    date: '2 hours ago',
    icon: '🍞'
  },
  {
    id: 2,
    description: 'Airtime MTN R50',
    amount: 50.00,
    type: 'income',
    category: 'AIRTIME',
    date: '4 hours ago',
    icon: '📱'
  },
  {
    id: 3,
    description: 'Stock purchase - Makro',
    amount: -500.00,
    type: 'expense',
    category: 'STOCK_PURCHASE',
    date: 'Yesterday',
    icon: '🛒'
  },
  {
    id: 4,
    description: 'Milk & sugar sales',
    amount: 85.00,
    type: 'income',
    category: 'GROCERIES',
    date: 'Yesterday',
    icon: '🥛'
  }
])

// Simulated grants
const eligibleGrants = ref([
  {
    id: 1,
    name: 'NYDA Business Grant',
    provider: 'National Youth Development Agency',
    amount: 'R10,000 - R100,000',
    match: 85,
    deadline: '30 days left',
    icon: '🎯'
  },
  {
    id: 2,
    name: 'SEFA Khula Loan',
    provider: 'Small Enterprise Finance Agency',
    amount: 'R5,000 - R3,000,000',
    match: 80,
    deadline: '60 days left',
    icon: '💼'
  },
  {
    id: 3,
    name: 'Township Fund',
    provider: 'Standard Bank',
    amount: 'R20,000 - R150,000',
    match: 100,
    deadline: '45 days left',
    icon: '🏦'
  }
])

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

// Quick actions
const quickActions = [
  {
    title: 'Add Transaction',
    description: 'Log a sale or expense',
    icon: '➕',
    color: 'primary',
    action: () => console.log('Add transaction')
  },
  {
    title: 'Ask Biz-Bantu',
    description: 'Get AI business advice',
    icon: '🤖',
    color: 'success',
    action: () => console.log('Open Biz-Bantu')
  },
  {
    title: 'View Grants',
    description: 'Browse funding options',
    icon: '🌱',
    color: 'accent',
    action: () => console.log('View grants')
  },
  {
    title: 'Reconcile Cash',
    description: 'Count your money',
    icon: '📊',
    color: 'neutral',
    action: () => console.log('Reconcile')
  }
]
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- GREETING SECTION -->
    <div>
      <h1 class="text-2xl lg:text-3xl font-bold text-neutral-900">
        {{ greeting }}
      </h1>
      <p class="text-sm lg:text-base text-neutral-600 mt-1">
        {{ userData.businessName }} • {{ userData.location }}
      </p>
    </div>

    <!-- EMPOWERSCORE CARD -->
    <EmpowerScoreCard
      :score="userData.score"
      :tier="userData.tier"
      :balance="userData.balance"
      :cash-balance="userData.cashBalance"
      :digital-balance="userData.digitalBalance"
    />

    <!-- QUICK ACTIONS -->
    <section>
      <h2 class="text-lg font-semibold text-neutral-900 mb-4">
        Quick Actions
      </h2>
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

    <!-- RECENT TRANSACTIONS -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-neutral-900">
          Recent Activity
        </h2>
        <button class="text-sm font-medium text-primary hover:text-primary-dark transition-colors">
          View All →
        </button>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-neutral-200 divide-y divide-neutral-100">
        <TransactionItem
          v-for="transaction in recentTransactions"
          :key="transaction.id"
          :transaction="transaction"
        />
      </div>
    </section>

    <!-- GRANTS CAROUSEL -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-neutral-900">
          🌱 Grants You Qualify For
        </h2>
        <button class="text-sm font-medium text-success hover:text-success-dark transition-colors">
          See All →
        </button>
      </div>

      <div class="lg:grid lg:grid-cols-3 lg:gap-4 flex lg:flex-none gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-4 px-4 lg:mx-0 lg:px-0">
        <GrantCard
          v-for="grant in eligibleGrants"
          :key="grant.id"
          :grant="grant"
          class="flex-shrink-0 w-80 lg:w-auto"
        />
      </div>
    </section>

    <!-- TIPS SECTION -->
    <section class="bg-gradient-to-br from-primary-light/10 to-accent/10 rounded-xl p-6 border border-primary/20">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl flex-shrink-0">
          💡
        </div>
        <div class="flex-1">
          <h3 class="font-semibold text-neutral-900 mb-2">
            Tip to Boost Your Score
          </h3>
          <p class="text-sm text-neutral-700 leading-relaxed">
            Your consistency score is great (83%)! To reach PRIME tier, 
            try adding 2-3 new product lines. This will improve your 
            diversity score by 15-20 points. 🚀
          </p>
        </div>
      </div>
    </section>
  </div>
</template>