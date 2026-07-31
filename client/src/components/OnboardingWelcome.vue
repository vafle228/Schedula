<script setup>
/* First-launch welcome screen. Mounted once in App.vue; visibility and every
   action live in useOnboarding.js so any component can reopen it. */
import { ref, watch } from 'vue'
import ModalWindow from './ModalWindow.vue'
import { useOnboarding } from '../composables/useOnboarding.js'

const ob = useOnboarding()
const state = ob.state

/* 'demo' | 'clean' — chosen but not yet applied */
const choice = ref('demo')

watch(() => state.welcome, (open) => {
  if (open) choice.value = 'demo'
})

const start = () => (choice.value === 'clean' ? ob.chooseClean() : ob.chooseDemo())
</script>

<template>
  <ModalWindow
    v-if="state.welcome"
    :width="620"
    @close="ob.skipWelcome()"
  >
    <template #title>
      <div class="head-main">
        <span class="head-title">Добро пожаловать в Schedula</span>
        <span class="head-sub">Распределение нагрузки и построение расписания</span>
      </div>
    </template>

    <div class="body">
      <p class="lead">
        Программа проведёт вас по всем разделам — от настроек учебного года до готовой
        сетки расписания. Займёт пару минут, пройти заново можно в любой момент.
      </p>

      <div class="micro">С ЧЕГО НАЧАТЬ</div>

      <button
        class="pick-soft opt"
        :class="{ on: choice === 'demo' }"
        @click="choice = 'demo'"
      >
        <span class="opt-title">Познакомиться на демо-данных</span>
        <span class="opt-sub">
          В базе уже есть учебный год, преподаватели, группы и дисциплины — удобно, чтобы
          посмотреть, как всё устроено. Ничего не удаляется.
        </span>
      </button>

      <button
        class="pick-soft opt"
        :class="{ on: choice === 'clean' }"
        :disabled="!state.canStartClean"
        @click="state.canStartClean && (choice = 'clean')"
      >
        <span class="opt-title">Начать с чистого листа</span>
        <span class="opt-sub">
          Удалить демонстрационные данные и создать пустой учебный год. Типы занятий
          сохранятся.
        </span>
        <span v-if="!state.canStartClean" class="opt-lock">
          недоступно — в базе есть ваши данные, удалять их программа не станет
        </span>
      </button>

      <div v-if="state.error" class="form-err">{{ state.error }}</div>
    </div>

    <template #footer>
      <span class="sp"></span>
      <button class="btn btn-lg" :disabled="state.busy" @click="ob.skipWelcome()">
        Пропустить
      </button>
      <button class="btn-primary btn-lg" :disabled="state.busy" @click="start">
        {{ state.busy ? 'Готовим…' : 'Начать обучение' }}
      </button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.head-main { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.head-title { font-size: 15px; font-weight: 600; }
.head-sub { font-size: 11.5px; color: var(--muted); }

.body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.lead { margin: 0; font-size: 12.5px; line-height: 1.5; color: var(--sub); }

.opt {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  text-align: left;
  padding: 12px 14px;
  width: 100%;
}
.opt:disabled { opacity: 0.55; cursor: not-allowed; }
.opt-title { font-size: 13px; font-weight: 600; }
.opt-sub { font-size: 11.5px; line-height: 1.45; color: var(--muted); }
.opt-lock {
  font: 500 10.5px var(--mono);
  color: var(--amber-dark);
  letter-spacing: 0.02em;
  margin-top: 2px;
}
.sp { flex: 1; }
</style>
