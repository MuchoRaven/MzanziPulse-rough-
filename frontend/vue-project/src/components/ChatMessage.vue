<!-- ═══════════════════════════════════════════════════════════════════════
     COMPONENT: Chat Message Bubble
     PURPOSE: Displays individual messages in WhatsApp-style
     ═══════════════════════════════════════════════════════════════════════ -->

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
    // Expected shape:
    // {
    //   role: 'user' | 'assistant',
    //   content: 'message text',
    //   timestamp: '10:30 AM',
    //   suggestions?: ['follow up 1', 'follow up 2']
    // }
  }
})

const isUser = computed(() => props.message.role === 'user')
const isBot = computed(() => props.message.role === 'assistant')

const emit = defineEmits(['suggestion-clicked'])

const handleSuggestionClick = (suggestion) => {
  emit('suggestion-clicked', suggestion)
}
</script>

<template>
  <div :class="['flex gap-3 mb-4 animate-fade-in', isUser ? 'flex-row-reverse' : 'flex-row']">
    <!-- ═══════════════════════════════════════════════════════════════════
         AVATAR
         User: Primary orange circle
         Bot: Success green circle with robot emoji
         ═══════════════════════════════════════════════════════════════════ -->
    <div class="flex-shrink-0">
      <div :class="[
        'w-10 h-10 rounded-full flex items-center justify-center text-xl',
        isUser ? 'bg-primary' : 'bg-gradient-to-br from-success to-success-dark'
      ]">
        <span class="text-white">{{ isUser ? '👤' : '🤖' }}</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════
         MESSAGE BUBBLE
         WhatsApp-style with tail on appropriate side
         ═══════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 max-w-[85%] lg:max-w-[70%]">
      <div :class="[
        'rounded-2xl px-4 py-3 shadow-sm',
        isUser 
          ? 'bg-primary text-white rounded-tr-none ml-auto'
          : 'bg-white border border-neutral-200 rounded-tl-none'
      ]">
        <!-- Message Content -->
        <div :class="[
          'text-sm leading-relaxed whitespace-pre-wrap',
          isUser ? 'text-white' : 'text-neutral-900'
        ]" v-html="message.content.replace(/\n/g, '<br>')">
        </div>

        <!-- Timestamp -->
        <div :class="[
          'text-xs mt-2 text-right',
          isUser ? 'text-orange-100' : 'text-neutral-400'
        ]">
          {{ message.timestamp }}
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════
           SUGGESTED FOLLOW-UP QUESTIONS (Bot messages only)
           ═══════════════════════════════════════════════════════════════ -->
      <div v-if="isBot && message.suggestions && message.suggestions.length > 0" 
           class="flex flex-wrap gap-2 mt-3">
        <button
          v-for="(suggestion, index) in message.suggestions"
          :key="index"
          @click="handleSuggestionClick(suggestion)"
          class="px-3 py-2 bg-white border-2 border-success text-success text-xs rounded-full hover:bg-success hover:text-white transition-all"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
  </div>
</template>

<!-- ═══════════════════════════════════════════════════════════════════════
     END: ChatMessage Component
     ═══════════════════════════════════════════════════════════════════════ -->