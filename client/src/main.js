import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router.js'
import { store } from './store/index.js'
import './styles/main.css'

async function bootstrap() {
  await store.init()
  createApp(App).use(router).mount('#app')
}

bootstrap()
