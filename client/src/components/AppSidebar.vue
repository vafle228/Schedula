<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store/index.js'

const route = useRoute()
const isOn = (name) => route.name === name
const orphanN = computed(() => store.scheduleAnalysis.value.orphanN)
</script>

<template>
  <nav class="rail">
    <div class="logo">УП</div>

    <router-link
      to="/distribution"
      class="rail-item"
      :class="{ on: isOn('distribution') }"
      title="Распределение — учебный план и назначения"
    >
      <span class="ico ico-box"></span>
      <span class="cap">Распр.</span>
    </router-link>

    <router-link
      to="/schedule"
      class="rail-item"
      :class="{ on: isOn('schedule') }"
      title="Расписание — сетка дни × пары"
    >
      <span class="ico ico-box"><span class="dash"></span></span>
      <span class="cap">Расп.</span>
      <span v-if="orphanN > 0" class="badge">{{ orphanN }}</span>
    </router-link>

    <router-link
      to="/directory"
      class="rail-item"
      :class="{ on: isOn('directory') }"
      title="Справочники — специальности, преподаватели, аудитории"
    >
      <span class="ico ico-box ico-lines"><span class="line"></span><span class="line"></span></span>
      <span class="cap">Справ.</span>
    </router-link>

    <span class="spacer"></span>

    <router-link
      to="/settings"
      class="rail-item"
      :class="{ on: isOn('settings') }"
      title="Настройки — глобальный конфиг периода"
    >
      <span class="ico ico-round"><span class="dot"></span></span>
      <span class="cap">Настр.</span>
    </router-link>
  </nav>
</template>

<style scoped>
.rail {
  flex: none;
  width: 56px;
  background: var(--panel);
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0 12px;
  gap: 6px;
}
.logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--fg);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font: 600 11px var(--mono);
  margin-bottom: 8px;
}
.rail-item {
  position: relative;
  width: 44px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  text-decoration: none;
}
.rail-item:hover { background: var(--chip); text-decoration: none; }
.rail-item.on { background: var(--active); }
.cap { font-size: 8px; font-weight: 500; color: var(--sub); }
.rail-item.on .cap { font-weight: 600; color: var(--fg); }

.ico { width: 14px; height: 14px; border: 1.5px solid var(--sub); display: inline-flex; align-items: center; justify-content: center; }
.ico-box { border-radius: 3px; }
.ico-round { border-radius: 50%; }
.rail-item.on .ico { border-color: var(--fg); }
.dash { width: 8px; height: 1.5px; background: var(--sub); }
.rail-item.on .dash { background: var(--fg); }
.ico-lines { flex-direction: column; gap: 2px; }
.ico-lines .line { width: 8px; height: 1.5px; background: var(--sub); }
.rail-item.on .ico-lines .line { background: var(--fg); }
.dot { width: 4px; height: 4px; border-radius: 50%; background: var(--sub); }
.rail-item.on .dot { background: var(--fg); }

.spacer { flex: 1; }

.badge {
  position: absolute;
  top: -3px;
  right: -3px;
  min-width: 15px;
  height: 15px;
  border-radius: 8px;
  background: var(--red);
  color: #FFFFFF;
  font: 600 9px var(--mono);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 3px;
}
</style>
