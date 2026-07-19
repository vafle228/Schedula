import { createRouter, createWebHashHistory } from 'vue-router'
import DistributionView from './views/distribution/DistributionView.vue'
import ScheduleView from './views/schedule/ScheduleView.vue'
import DirectoryView from './views/directory/DirectoryView.vue'
import SettingsView from './views/settings/SettingsView.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/schedule' },
    { path: '/distribution', name: 'distribution', component: DistributionView },
    { path: '/schedule', name: 'schedule', component: ScheduleView },
    { path: '/directory', name: 'directory', component: DirectoryView },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})
