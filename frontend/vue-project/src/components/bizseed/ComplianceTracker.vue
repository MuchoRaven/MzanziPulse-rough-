<template>
  <div class="space-y-4">
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
      <p class="text-neutral-500 mt-4">Loading compliance status...</p>
    </div>

    <div v-else class="space-y-4">
      <!-- CIPC Registration -->
      <div class="border border-neutral-200 rounded-lg p-4">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ getStatusIcon(compliance.cipc.status) }}</span>
              <h4 class="font-bold text-neutral-900">CIPC Registration</h4>
            </div>
            <p class="text-sm text-neutral-600 mb-2">{{ compliance.cipc.action }}</p>
            <div class="flex gap-4 text-xs text-neutral-500">
              <span>💰 {{ compliance.cipc.estimatedCost }}</span>
              <span>⏱️ {{ compliance.cipc.estimatedTime }}</span>
            </div>
          </div>
          <a 
            href="https://eservices.cipc.co.za/"
            target="_blank"
            rel="noopener noreferrer"
            class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-2"
          >
            <span>Start Registration</span>
            <span class="text-lg">→</span>
          </a>
        </div>
      </div>

      <!-- SARS Tax -->
      <div class="border border-neutral-200 rounded-lg p-4">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ getStatusIcon(compliance.sars.status) }}</span>
              <h4 class="font-bold text-neutral-900">SARS Tax Number</h4>
            </div>
            <p class="text-sm text-neutral-600 mb-2">{{ compliance.sars.action }}</p>
            <div v-if="compliance.sars.taxClearanceExpiry" class="text-xs text-warning">
              ⚠️ Tax clearance expires: {{ compliance.sars.taxClearanceExpiry }}
            </div>
          </div>
          <a 
            href="https://www.sarsefiling.co.za/"
            target="_blank"
            rel="noopener noreferrer"
            class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-2"
          >
            <span>Register for Tax</span>
            <span class="text-lg">→</span>
          </a>
        </div>
      </div>

      <!-- B-BBEE -->
      <div class="border border-neutral-200 rounded-lg p-4">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ getStatusIcon(compliance.bbbee.status) }}</span>
              <h4 class="font-bold text-neutral-900">B-BBEE Certificate</h4>
            </div>
            <p class="text-sm text-neutral-600 mb-2">{{ compliance.bbbee.action }}</p>
            <div class="flex gap-4 text-xs text-neutral-500">
              <span>💰 {{ compliance.bbbee.estimatedCost }}</span>
            </div>
          </div>
          <button
            @click="downloadBBBEETemplate"
            class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-2"
          >
            <span>Get Affidavit</span>
            <span class="text-lg">📄</span>
          </button>
        </div>
      </div>

      <!-- POPIA Compliance -->
      <div class="border border-neutral-200 rounded-lg p-4">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ getStatusIcon(compliance.popia.status) }}</span>
              <h4 class="font-bold text-neutral-900">POPIA Compliance</h4>
            </div>
            <p class="text-sm text-neutral-600 mb-2">{{ compliance.popia.action }}</p>
            <div class="flex gap-4 text-xs text-neutral-500">
              <span>💰 {{ compliance.popia.estimatedCost }}</span>
            </div>
          </div>
          <button
            @click="downloadPOPIATemplates"
            class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors inline-flex items-center gap-2"
          >
            <span>Download Templates</span>
            <span class="text-lg">📄</span>
          </button>
        </div>
      </div>

      <!-- Overall Progress -->
      <div class="bg-neutral-50 rounded-lg p-4 mt-6">
        <h4 class="font-bold text-neutral-900 mb-3">Compliance Progress</h4>
        <div class="w-full bg-neutral-200 rounded-full h-3 overflow-hidden">
          <div 
            class="progress-bar-fill bg-primary h-full transition-all duration-500"
            :style="{ width: `${compliance.overallScore}%` }"
          ></div>
        </div>
        <p class="text-sm text-neutral-600 mt-2">
          {{ compliance.overallScore }}% Complete - {{ compliance.readinessLevel }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, onMounted } from 'vue'

const props = defineProps({
  userId: Number
})

const loading = ref(true)
const compliance = ref({
  cipc: {
    status: 'NOT_REGISTERED',
    action: 'Register your business with CIPC',
    estimatedCost: 'R175 - R500',
    estimatedTime: '2-5 business days'
  },
  sars: {
    status: 'NOT_REGISTERED',
    action: 'Register for Income Tax',
    taxClearanceExpiry: null
  },
  bbbee: {
    status: 'NOT_STARTED',
    action: 'Get EME Affidavit (R0 - R10M turnover)',
    estimatedCost: 'R500 - R2,000'
  },
  popia: {
    status: 'PARTIAL',
    action: 'Implement customer consent system',
    estimatedCost: 'R0 (DIY Template)'
  },
  overallScore: 15,
  readinessLevel: 'INFORMAL'
})

const fetchCompliance = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/compliance/status/${props.userId}`)
    const data = await response.json()
    
    if (data.success) {
      compliance.value = data.compliance
    }
  } catch (error) {
    console.error('Failed to fetch compliance:', error)
  } finally {
    loading.value = false
  }
}

const getStatusIcon = (status) => {
  const icons = {
    'NOT_REGISTERED': '❌',
    'NOT_STARTED': '⏸️',
    'PARTIAL': '🔄',
    'IN_PROGRESS': '⏳',
    'REGISTERED': '✅',
    'VERIFIED': '✅',
    'NOT_APPLICABLE': 'ℹ️'
  }
  return icons[status] || '❓'
}

const downloadBBBEETemplate = () => {
  const templateContent = `B-BBEE EME AFFIDAVIT TEMPLATE

I, _________________________________ (Full Name)
ID Number: _______________________
Acting in my capacity as: _______________________

Do hereby make oath and state that:

1. I am the owner/director of _________________________________ (Business Name)
   Registration Number: _______________________

2. The annual turnover of the business for the last financial year did not exceed R10,000,000 (Ten Million Rands).

3. I am a South African citizen/permanent resident.

4. This affidavit is made for the purpose of claiming Exempted Micro Enterprise (EME) status in terms of the B-BBEE Codes.

5. I understand that making a false declaration is an offense.


_____________________          _____________________
Signature                      Date


COMMISSIONER OF OATHS:
_____________________
Signature & Stamp


---
INSTRUCTIONS:
1. Fill in all fields
2. Sign in front of a Commissioner of Oaths
3. Attach copy of ID
4. Attach proof of turnover (bank statements or financial statements)
5. Submit to clients when required

Note: This affidavit is valid for 12 months from date of signing.
`
  
  const blob = new Blob([templateContent], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'BBBEE_EME_Affidavit_Template.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
  
  alert('✅ B-BBEE EME Affidavit template downloaded! Fill it out and get it signed by a Commissioner of Oaths.')
}

const downloadPOPIATemplates = () => {
  const templateContent = `POPIA COMPLIANCE TEMPLATES

=== 1. PRIVACY POLICY ===

[Business Name] Privacy Policy

We collect and process personal information in accordance with the Protection of Personal Information Act (POPIA).

Information We Collect:
- Name and contact details
- Purchase history
- Payment information

How We Use Your Information:
- To process transactions
- To communicate about products/services
- To improve our services

Your Rights:
- Access your personal information
- Request correction of information
- Object to processing
- Lodge complaints with the Information Regulator

Contact our Information Officer:
Email: ___________________
Phone: ___________________


=== 2. CUSTOMER CONSENT FORM ===

CONSENT TO PROCESS PERSONAL INFORMATION

I, _______________________ (Full Name)
ID Number: _________________
Contact: ___________________

Hereby consent to [Business Name] collecting and processing my personal information for the following purposes:

☐ Processing transactions
☐ Marketing communications
☐ Customer service

I understand that:
- I can withdraw this consent at any time
- My information will be kept secure
- I have the right to access my information

Signature: ________________  Date: __________


=== 3. DATA BREACH PROCEDURE ===

1. IDENTIFY: Detect unauthorized access
2. CONTAIN: Stop the breach immediately
3. ASSESS: Determine what data was affected
4. NOTIFY: Inform affected individuals within 24 hours
5. REPORT: Report to Information Regulator if serious
6. REMEDY: Take steps to prevent recurrence
7. DOCUMENT: Keep records of the incident


Save these templates and customize them for your business.
`

  const blob = new Blob([templateContent], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'POPIA_Compliance_Templates.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
  
  alert('✅ POPIA templates downloaded! Customize them for your business and implement them.')
}

onMounted(() => {
  fetchCompliance()
})
</script>