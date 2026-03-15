<template>
  <div class="space-y-4">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-success mx-auto"></div>
      <p class="text-neutral-500 mt-4">Finding funding matched to your profile...</p>
    </div>

    <div v-else class="space-y-4">

      <!-- Profile snapshot -->
      <div v-if="profile" class="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
        <p class="text-xs font-semibold text-neutral-500 uppercase tracking-wide mb-3">Your Funding Profile</p>
        <div class="flex flex-wrap gap-2">
          <span v-if="profile.isYouth"    class="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full font-medium">🎓 Youth (≤35)</span>
          <span v-if="profile.isFemale"   class="px-2 py-1 bg-accent/10 text-accent text-xs rounded-full font-medium">👩 Women-owned</span>
          <span v-if="profile.isTownship" class="px-2 py-1 bg-success/10 text-success text-xs rounded-full font-medium">🏘️ Township Business</span>
          <span v-if="profile.isFormal"   class="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full font-medium">✅ CIPC Registered</span>
          <span v-if="!profile.isFormal"  class="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full font-medium">⚠️ Not Yet Formal</span>
          <span class="px-2 py-1 bg-neutral-200 text-neutral-700 text-xs rounded-full font-medium">
            💰 R{{ formatAmount(profile.monthlyTurnover) }}/month
          </span>
          <span v-if="profile.age" class="px-2 py-1 bg-neutral-200 text-neutral-700 text-xs rounded-full font-medium">
            🎂 Age {{ profile.age }}
          </span>
          <span class="px-2 py-1 bg-neutral-200 text-neutral-700 text-xs rounded-full font-medium">
            📍 {{ profile.township || profile.province }}
          </span>
        </div>
      </div>

      <!-- Funding summary — only counts GRANTS in the total -->
      <div class="bg-gradient-to-br from-success/5 to-primary/5 rounded-xl p-4 border border-success/20">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-neutral-600">Non-repayable Grants You Qualify For</p>
            <p class="text-3xl font-bold text-success">R{{ grantTotal.toLocaleString('en-ZA') }}</p>
            <p class="text-xs text-neutral-400 mt-0.5">Grants only — does not include loans</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-neutral-600">Funding Options</p>
            <p class="text-3xl font-bold text-primary">{{ eligibleCount }}</p>
            <p class="text-xs text-neutral-400 mt-0.5">grants + loans</p>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-3 text-xs">
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-success inline-block"></span> Non-repayable grant</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-primary inline-block"></span> Loan (must repay)</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-accent inline-block"></span> Revenue advance</span>
      </div>

      <!-- Funding cards -->
      <div class="space-y-3">
        <div
          v-for="grant in grants"
          :key="grant.id"
          class="border rounded-xl p-4 transition-colors"
          :class="grant.eligible
            ? 'border-success/40 bg-success/5'
            : 'border-neutral-200 bg-white'"
        >
          <!-- Header row -->
          <div class="flex items-start justify-between gap-3 mb-2">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <h5 class="font-bold text-neutral-900">{{ grant.name }}</h5>

                <!-- Funding type badge -->
                <span
                  class="px-2 py-0.5 text-xs rounded-full font-bold uppercase tracking-wide"
                  :class="fundingTypeClass(grant.fundingType)"
                >{{ fundingTypeLabel(grant.fundingType) }}</span>

                <!-- Match badge -->
                <span
                  class="px-2 py-0.5 text-xs rounded-full font-semibold"
                  :class="grant.match >= 80 ? 'bg-success/20 text-success'
                        : grant.match >= 60 ? 'bg-primary/20 text-primary'
                        : 'bg-warning/20 text-warning'"
                >
                  {{ grant.match }}% match
                </span>

                <!-- Tags -->
                <span
                  v-for="tag in grant.tags"
                  :key="tag"
                  class="px-2 py-0.5 text-xs bg-neutral-100 text-neutral-600 rounded-full"
                >{{ tag }}</span>
              </div>
              <p class="text-sm text-neutral-500">{{ grant.provider }}</p>
            </div>
            <div class="text-right shrink-0">
              <p class="text-base font-bold" :class="grant.fundingType === 'GRANT' ? 'text-success' : 'text-primary'">
                R{{ grant.amount.min.toLocaleString('en-ZA') }}
                <span v-if="grant.amount.max !== grant.amount.min">– R{{ grant.amount.max.toLocaleString('en-ZA') }}</span>
              </p>
              <p class="text-xs text-neutral-400 mt-0.5 max-w-[140px] text-right">{{ grant.deadlineLabel }}</p>
            </div>
          </div>

          <p class="text-sm text-neutral-700 mb-3">{{ grant.description }}</p>

          <!-- Honest notes / disclaimer -->
          <div v-if="grant.notes" class="mb-3 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <p class="text-xs text-amber-800 leading-relaxed">
              <span class="font-semibold">ℹ️ Note: </span>{{ grant.notes }}
            </p>
          </div>

          <!-- Eligible: why you qualify -->
          <div v-if="grant.eligible && grant.qualifyReasons.length" class="mb-3 space-y-1">
            <p class="text-xs font-semibold text-success uppercase tracking-wide">Why you qualify</p>
            <ul class="space-y-0.5">
              <li
                v-for="r in grant.qualifyReasons"
                :key="r"
                class="flex items-start gap-1.5 text-sm text-neutral-700"
              >
                <span class="text-success mt-0.5">✓</span> {{ r }}
              </li>
            </ul>
          </div>

          <!-- Not eligible: what's missing -->
          <div v-else-if="!grant.eligible && grant.failReasons.length" class="mb-3 space-y-1">
            <p class="text-xs font-semibold text-warning uppercase tracking-wide">What you still need</p>
            <ul class="space-y-0.5">
              <li
                v-for="r in grant.failReasons"
                :key="r"
                class="flex items-start gap-1.5 text-sm text-neutral-600"
              >
                <span class="text-warning mt-0.5">•</span> {{ r }}
              </li>
            </ul>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap gap-2 mt-2">
            <a
              v-if="grant.eligible"
              :href="grant.applicationUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="px-4 py-2 bg-success hover:bg-success-dark text-white rounded-lg text-sm font-medium transition-colors"
            >
              {{ grant.fundingType === 'GRANT' ? 'Apply Now →' : 'Apply for Loan →' }}
            </a>
            <a
              :href="grant.applicationUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm font-medium transition-colors"
            >
              {{ grant.eligible ? 'Official Site ↗' : 'Learn More ↗' }}
            </a>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="grants.length === 0" class="text-center py-10">
        <span class="text-6xl mb-4 block">🔍</span>
        <p class="text-neutral-600 font-medium">No matching funding found right now</p>
        <p class="text-sm text-neutral-500 mt-2">
          Register your business with CIPC to unlock more funding opportunities.
        </p>
      </div>

      <!-- Disclaimer footer -->
      <div class="bg-neutral-100 rounded-xl p-4 text-xs text-neutral-500 leading-relaxed">
        <p class="font-semibold text-neutral-600 mb-1">⚖️ Important Disclaimer</p>
        <p>
          Funding information is based on publicly available programme details (verified 2025/2026).
          Eligibility criteria, amounts, and deadlines may change — always verify directly with the funding provider
          before investing time in an application.
          Loans must be repaid; grants do not.
          MzansiPulse is not a funding intermediary and cannot guarantee approval.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({ userId: Number })

const loading  = ref(true)
const grants   = ref([])
const profile  = ref(null)

const eligibleCount = computed(() => grants.value.filter(g => g.eligible).length)

// Only sum non-repayable grants (not loans) for the headline figure
const grantTotal = computed(() =>
  grants.value
    .filter(g => g.eligible && g.fundingType === 'GRANT')
    .reduce((s, g) => s + g.amount.max, 0)
)

const fetchGrants = async () => {
  loading.value = true
  try {
    const res  = await fetch(`http://localhost:5000/api/bizseed/grants/matches/${props.userId}`)
    const data = await res.json()
    if (data.success) {
      grants.value  = data.grants
      profile.value = data.profile
    }
  } catch (e) {
    console.error('Failed to fetch grants:', e)
  } finally {
    loading.value = false
  }
}

const fundingTypeLabel = (type) => {
  if (type === 'GRANT')           return 'Grant'
  if (type === 'REVENUE_ADVANCE') return 'Revenue Advance'
  return 'Loan'
}

const fundingTypeClass = (type) => {
  if (type === 'GRANT')           return 'bg-success/20 text-success'
  if (type === 'REVENUE_ADVANCE') return 'bg-accent/20 text-accent'
  return 'bg-primary/20 text-primary'
}

const formatAmount = (n) => {
  if (!n) return '0'
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K'
  return n.toLocaleString('en-ZA')
}

onMounted(fetchGrants)
</script>
