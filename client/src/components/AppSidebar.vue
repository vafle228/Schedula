<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store/index.js'
import { useOnboarding } from '../composables/useOnboarding.js'
import iconUrl from '../static/icon.png'

const route = useRoute()
const isOn = (name) => route.name === name
const orphanN = computed(() => store.scheduleAnalysis.value.orphanN)

const ob = useOnboarding()
/* Nudge the button while the tour has never been finished. */
const obUnseen = computed(
  () => ob.state.status === 'pending' || ob.state.status === 'in_progress',
)

const collapsed = ref(localStorage.getItem('sidebarCollapsed') === '1')
const toggle = () => { collapsed.value = !collapsed.value }
watch(collapsed, (v) => localStorage.setItem('sidebarCollapsed', v ? '1' : '0'))
</script>

<template>
  <nav class="rail" :class="{ collapsed }">
    <div class="brand">
      <img class="logo" :src="iconUrl" alt="Schedula" />
      <span class="brand-name">Schedula</span>
      <button
        class="fold"
        :title="collapsed ? 'Развернуть' : 'Свернуть'"
        :aria-label="collapsed ? 'Развернуть меню' : 'Свернуть меню'"
        @click="toggle"
      >
        <svg class="fold-ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M15 6l-6 6 6 6" />
        </svg>
      </button>
    </div>

    <div class="nav">
      <router-link
        to="/distribution"
        class="rail-item"
        :class="{ on: isOn('distribution') }"
        title="Распределение — учебный план и назначения"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" />
          <rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
        <span class="cap">Распределение</span>
      </router-link>

      <router-link
        to="/schedule"
        class="rail-item"
        :class="{ on: isOn('schedule') }"
        title="Расписание — сетка дни × пары"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="3" y="4.5" width="18" height="16" rx="2" />
          <path d="M3 9h18" />
          <path d="M8 2.5v4M16 2.5v4" />
        </svg>
        <span class="cap">Расписание</span>
        <span v-if="orphanN > 0" class="badge">{{ orphanN }}</span>
      </router-link>

      <router-link
        to="/directory"
        class="rail-item"
        :class="{ on: isOn('directory') }"
        title="Справочники — специальности, преподаватели, аудитории"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H19a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H5.5A1.5 1.5 0 0 1 4 18.5z" />
          <path d="M4 17.5A1.5 1.5 0 0 1 5.5 16H20" />
          <path d="M8 7.5h7M8 11h5" />
        </svg>
        <span class="cap">Справочники</span>
      </router-link>
    </div>

    <span class="spacer"></span>

    <div class="nav">
      <button
        class="rail-item rail-btn"
        title="Обучение — пройти знакомство с программой заново"
        @click="ob.openTour()"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M9.2 9.3a2.9 2.9 0 1 1 3.9 2.7c-.7.3-1.1.9-1.1 1.6v.4" />
          <path d="M12 17.2h.01" />
        </svg>
        <span class="cap">Обучение</span>
        <span v-if="obUnseen" class="dot"></span>
      </button>

      <router-link
        to="/settings"
        class="rail-item"
        :class="{ on: isOn('settings') }"
        title="Настройки — глобальный конфиг периода"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
        <span class="cap">Настройки</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.rail {
  flex: none;
  width: 188px;
  background: var(--panel);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  padding: 14px 10px 14px;
  gap: 4px;
  transition: width 0.18s ease;
}
.rail.collapsed { width: 64px; }

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 6px 14px;
}
.rail.collapsed .brand {
  flex-direction: column;
  gap: 8px;
  padding: 0 0 14px;
}
.rail.collapsed .brand-name { display: none; }

.fold {
  margin-left: auto;
  flex: none;
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  border-radius: var(--r-md);
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}
.fold:hover { background: var(--hover); color: var(--fg); }
.rail.collapsed .fold { margin-left: 0; }
.fold-ico {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: transform 0.18s ease;
}
.rail.collapsed .fold-ico { transform: rotate(180deg); }
.logo {
  flex: none;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  object-fit: contain;
  display: block;
}
.brand-name {
  font: 600 15px var(--sans);
  color: var(--fg);
  letter-spacing: -0.01em;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rail-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  height: 38px;
  padding: 0 10px;
  border-radius: var(--r-lg);
  text-decoration: none;
  color: var(--sub);
}
.rail-item:hover { background: var(--hover); color: var(--fg); text-decoration: none; }
.rail-item.on { background: var(--active); color: var(--fg); }
.rail.collapsed .rail-item {
  justify-content: center;
  gap: 0;
  padding: 0;
}

/* The tour opens an overlay rather than a route, so it is a button — reset the
   UA styles that <a> does not carry. */
.rail-btn {
  border: none;
  background: none;
  width: 100%;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.dot {
  margin-left: auto;
  flex: none;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--blue);
}
.rail.collapsed .dot {
  position: absolute;
  top: 6px;
  right: 12px;
  margin-left: 0;
}

.cap {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
}
.rail-item.on .cap { font-weight: 600; }
.rail.collapsed .cap { display: none; }

.ico {
  flex: none;
  width: 19px;
  height: 19px;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.spacer { flex: 1; }

.badge {
  margin-left: auto;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: var(--red);
  color: #FFFFFF;
  font: 600 10px var(--mono);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}
.rail.collapsed .badge {
  position: absolute;
  top: 2px;
  right: 8px;
  margin-left: 0;
  min-width: 15px;
  height: 15px;
  padding: 0 4px;
  font-size: 9px;
}
</style>
