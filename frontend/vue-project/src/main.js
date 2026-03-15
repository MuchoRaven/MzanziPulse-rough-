import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'

import App from './App.vue'
import router from './router'

import en from './locales/en.json'
import zu from './locales/zu.json'
import st from './locales/st.json'
import xh from './locales/xh.json'

// Restore saved language preference (falls back to 'en')
const savedLocale = localStorage.getItem('mp_locale') || 'en'

const i18n = createI18n({
  legacy: false,          // Use Composition API mode
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, zu, st, xh }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
