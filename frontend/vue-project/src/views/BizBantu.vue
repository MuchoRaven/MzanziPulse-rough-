<!-- ═══════════════════════════════════════════════════════════════════════
     PAGE: Biz-Bantu AI Chat Interface
     PURPOSE: WhatsApp-style chat with AI business advisor
     FEATURES:
     - Real-time chat with Pangu AI
     - Context-aware responses (uses user's business data)
     - Multilingual support
     - Suggested follow-up questions
     - Chat history persistence
     ═══════════════════════════════════════════════════════════════════════ -->

<script setup>
import API_BASE from '@/config/api'
import { ref, computed, nextTick, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import ChatMessage from '../components/ChatMessage.vue'

const authStore = useAuthStore()

// ═══════════════════════════════════════════════════════════════════════════
// STATE MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const chatContainer = ref(null)

// Language selection
const selectedLanguage = ref(localStorage.getItem('mzansi_chat_language') || 'en')
const showLanguageSelector = ref(false)

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'zu', name: 'isiZulu', flag: '🇿🇦' },
  { code: 'st', name: 'Sesotho', flag: '🇿🇦' },
  { code: 'xh', name: 'isiXhosa', flag: '🇿🇦' }
]

const setLanguage = (langCode) => {
  selectedLanguage.value = langCode
  localStorage.setItem('mzansi_chat_language', langCode)
  showLanguageSelector.value = false
  
  // Show language change confirmation
  const confirmMsg = {
    'en': 'Language changed to English',
    'zu': 'Ulimi luguqulwe lwaba isiZulu',
    'st': 'Puo e fetotse ho Sesotho',
    'xh': 'Ulwimi lutshintshwe lwaba isiXhosa'
  }
  
  // Could add a toast notification here
  console.log(confirmMsg[langCode])
}

// Update userContext to include selected language
const userContext = computed(() => ({
  userId: authStore.user?.id,
  firstName: authStore.user?.firstName,
  lastName: authStore.user?.lastName,
  businessId: authStore.user?.businessId,
  businessName: authStore.user?.businessName,
  businessType: authStore.user?.businessType,
  location: authStore.user?.location,
  empowerScore: 542,
  language: selectedLanguage.value  // ✅ NOW PERSISTENT!
}))

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

onMounted(() => {
  // Load chat history from localStorage
  loadChatHistory()
  
  // Send welcome message if first time
  if (messages.value.length === 0) {
    sendWelcomeMessage()
  }
  
  // Scroll to bottom
  scrollToBottom()
})

// ═══════════════════════════════════════════════════════════════════════════
// CORE CHAT FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

const sendMessage = async () => {
  const messageText = userInput.value.trim()
  
  if (!messageText || isLoading.value) return
  
  // Add user message to chat
  const userMessage = {
    role: 'user',
    content: messageText,
    timestamp: getCurrentTime()
  }
  
  messages.value.push(userMessage)
  userInput.value = ''
  
  // Scroll to show new message
  await nextTick()
  scrollToBottom()
  
  // Show loading state
  isLoading.value = true
  
  try {
    // Call backend API
    const response = await fetch('${API_BASE}/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: messageText,
        userContext: userContext.value,
        chatHistory: messages.value.slice(-5) // Last 5 messages for context
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      // Add bot response
      const botMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: getCurrentTime(),
        suggestions: data.suggestions || []
      }
      
      messages.value.push(botMessage)
      
      // Save chat history
      saveChatHistory()
      
      // Scroll to show response
      await nextTick()
      scrollToBottom()
    } else {
      throw new Error(data.error || 'Failed to get response')
    }
    
  } catch (error) {
    console.error('Chat error:', error)
    
    // Add error message
    const errorMessage = {
      role: 'assistant',
      content: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
      timestamp: getCurrentTime()
    }
    
    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
  }
}

const handleSuggestionClick = (suggestion) => {
  userInput.value = suggestion
  sendMessage()
}

const sendWelcomeMessage = () => {
  const name = userContext.value.firstName || 'there'
  const welcomeMessage = {
    role: 'assistant',
    content: `Hello ${name}! 👋

I'm **Biz-Bantu**, your AI business advisor!

I'm here to help you grow ${userContext.value.businessName || 'your business'}. I can help you with:

💰 Finding grants and funding
📈 Increasing sales and customers  
📊 Managing cash flow
🎯 Improving your EmpowerScore
📓 Managing 'book' credit
🏪 Stock management tips

**Ask me anything!** What would you like help with today?`,
    timestamp: getCurrentTime(),
    suggestions: [
      "Show me funding options",
      "How can I increase sales?",
      "What's my EmpowerScore?",
      "Help with cash flow"
    ]
  }
  
  messages.value.push(welcomeMessage)
  saveChatHistory()
}

const clearChat = () => {
  if (confirm('Clear chat history? This cannot be undone.')) {
    messages.value = []
    localStorage.removeItem(chatKey())
    sendWelcomeMessage()
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  })
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const chatKey = () => `mzansi_chat_history_${authStore.user?.id}`

const saveChatHistory = () => {
  try {
    localStorage.setItem(chatKey(), JSON.stringify(messages.value))
  } catch (e) {
    console.error('Failed to save chat history:', e)
  }
}

const loadChatHistory = () => {
  try {
    const saved = localStorage.getItem(chatKey())
    if (saved) {
      messages.value = JSON.parse(saved)
    }
  } catch (e) {
    console.error('Failed to load chat history:', e)
  }
}

// Quick action buttons
const quickActions = [
  { icon: '💰', text: 'Funding', message: 'Show me funding options' },
  { icon: '📈', text: 'Sales', message: 'How can I increase sales?' },
  { icon: '📊', text: 'Cash Flow', message: 'Help with cash management' },
  { icon: '🎯', text: 'Score', message: "What's my EmpowerScore?" }
]

const sendQuickAction = (action) => {
  userInput.value = action.message
  sendMessage()
}
</script>

<template>
  <!-- ═══════════════════════════════════════════════════════════════════
       MAIN CHAT CONTAINER
       ═══════════════════════════════════════════════════════════════════ -->
  
  <div class="flex flex-col h-[calc(100vh-8rem)] lg:h-[calc(100vh-4rem)] bg-neutral-50">
    
    <!-- CHAT HEADER - Add language selector -->
    <div class="bg-gradient-to-r from-success to-success-dark text-white px-4 py-4 shadow-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-2xl">
            🤖
          </div>
          <div>
            <h1 class="text-lg font-bold">Biz-Bantu AI</h1>
            <p class="text-xs text-green-100">Your Business Advisor • Always Online</p>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- Language Selector Button -->
          <button 
            @click="showLanguageSelector = !showLanguageSelector"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors relative"
            title="Change Language"
          >
            <span class="text-xl">🌍</span>
            
            <!-- Language Dropdown -->
            <div 
              v-if="showLanguageSelector"
              class="absolute right-0 top-full mt-2 bg-white rounded-lg shadow-xl border border-neutral-200 py-2 z-50 min-w-[160px]"
              @click.stop
            >
              <button
                v-for="lang in languages"
                :key="lang.code"
                @click="setLanguage(lang.code)"
                :class="[
                  'w-full px-4 py-2 text-left hover:bg-neutral-100 transition-colors flex items-center gap-2',
                  selectedLanguage === lang.code ? 'bg-success/10 text-success' : 'text-neutral-700'
                ]"
              >
                <span class="text-lg">{{ lang.flag }}</span>
                <span class="text-sm font-medium">{{ lang.name }}</span>
                <span v-if="selectedLanguage === lang.code" class="ml-auto text-success">✓</span>
              </button>
            </div>
          </button>
          
          <!-- Clear Chat Button -->
          <button 
            @click="clearChat"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="Clear chat"
          >
            <span class="text-xl">🗑️</span>
          </button>
        </div>
      </div>

    <!-- Current Language Indicator -->
      <div class="mt-2 text-xs text-green-100">
        Language: {{ languages.find(l => l.code === selectedLanguage)?.name }};
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         QUICK ACTION BUTTONS (When chat is empty or few messages)
         ═══════════════════════════════════════════════════════════════ -->
    <div v-if="messages.length <= 1" class="px-4 py-4 bg-white border-b border-neutral-200">
      <p class="text-xs text-neutral-600 mb-3 font-medium">Quick Questions:</p>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
        <button
          v-for="action in quickActions"
          :key="action.text"
          @click="sendQuickAction(action)"
          class="flex items-center gap-2 px-3 py-2 bg-neutral-50 hover:bg-neutral-100 border border-neutral-200 rounded-lg transition-all text-left"
        >
          <span class="text-xl">{{ action.icon }}</span>
          <span class="text-xs font-medium text-neutral-700">{{ action.text }}</span>
        </button>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         MESSAGES AREA (Scrollable chat history)
         ═══════════════════════════════════════════════════════════════ -->
    <div 
      ref="chatContainer"
      class="flex-1 overflow-y-auto px-4 py-4 space-y-1 scrollbar-hide"
      style="background-image: url('data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23e5e5e5\' fill-opacity=\'0.1\'%3E%3Cpath d=\'M0 0h20v20H0V0zm10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14z\'/%3E%3C/g%3E%3C/svg%3E');"
    >
      <!-- Chat Messages -->
      <ChatMessage
        v-for="(message, index) in messages"
        :key="index"
        :message="message"
        @suggestion-clicked="handleSuggestionClick"
      />

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-success to-success-dark flex items-center justify-center text-white text-xl">
          🤖
        </div>
        <div class="bg-white border border-neutral-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
          <div class="flex gap-1">
            <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
            <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         MESSAGE INPUT AREA (Fixed at bottom)
         ═══════════════════════════════════════════════════════════════ -->
    <div class="bg-white border-t border-neutral-200 px-4 py-3 shadow-lg">
      <form @submit.prevent="sendMessage" class="flex gap-3">
        <input
          v-model="userInput"
          type="text"
          placeholder="Ask Biz-Bantu anything..."
          :disabled="isLoading"
          class="flex-1 px-4 py-3 rounded-full border border-neutral-300 focus:border-success focus:ring-2 focus:ring-success/20 outline-none transition-all disabled:bg-neutral-100 disabled:cursor-not-allowed"
        />
        
        <button
          type="submit"
          :disabled="!userInput.trim() || isLoading"
          :class="[
            'px-6 py-3 rounded-full font-semibold transition-all flex items-center gap-2',
            userInput.trim() && !isLoading
              ? 'bg-success text-white hover:bg-success-dark'
              : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
          ]"
        >
          <span>Send</span>
          <span class="text-lg">📤</span>
        </button>
      </form>
      
      <p class="text-xs text-neutral-500 text-center mt-2">
        Biz-Bantu can make mistakes. Verify important information.
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Custom bounce animation for loading dots */
@keyframes bounce {
  0%, 80%, 100% { 
    transform: translateY(0);
  }
  40% { 
    transform: translateY(-8px);
  }
}

.animate-bounce {
  animation: bounce 1.4s ease-in-out infinite;
}
</style>

<!-- ═══════════════════════════════════════════════════════════════════════
     END: Biz-Bantu Chat Page
     ═══════════════════════════════════════════════════════════════════════ -->