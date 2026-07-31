import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router.js'
import { store } from './store/index.js'
import { initOnboarding } from './composables/useOnboarding.js'
import './styles/main.css'

async function bootstrap() {
  // Both before mount: the welcome screen must be decided on the first paint,
  // not flash in a moment later.
  await Promise.all([store.init(), initOnboarding()])
  createApp(App).use(router).mount('#app')
}

bootstrap()
