<script setup>
import { reactive, computed } from 'vue'
import { store } from '../store/index.js'
import { ROOM_TYPES } from '../utils/kinds.js'
import { plural } from '../utils/format.js'

const form = reactive({ id: '', cap: '40', type: ROOM_TYPES[0], err: '' })

const usage = computed(() => {
  const m = {}
  store.state.lessons.forEach((l) => { m[l.roomId] = (m[l.roomId] || 0) + 1 })
  return m
})

const rows = computed(() => store.state.rooms.map((r) => {
  const used = usage.value[r.id] || 0
  return {
    ...r,
    used,
    usageLabel: used ? used + ' ' + plural(used, 'пара', 'пары', 'пар') + '/нед' : 'свободна',
    delTip: used ? 'Нельзя удалить: на аудиторию назначены пары' : 'Удалить аудиторию',
  }
}))

async function add() {
  const id = form.id.trim()
  if (!id) { form.err = 'Укажите номер или название аудитории'; return }
  if (store.state.rooms.some((r) => r.id.toLowerCase() === id.toLowerCase())) {
    form.err = 'Аудитория «' + id + '» уже есть в справочнике'
    return
  }
  const capacity = Math.max(1, parseInt(form.cap, 10) || 1)
  await store.createRoom({ id, capacity, type: form.type })
  form.id = ''
  form.err = ''
}

function del(r) {
  if (r.used) return
  store.deleteRoom(r.id)
}
</script>

<template>
  <div class="rooms">
    <div class="new-room">
      <div class="micro">НОВАЯ АУДИТОРИЯ</div>
      <div class="new-row">
        <input
          v-model="form.id"
          class="input input--white id-input"
          placeholder="Номер / название"
          @input="form.err = ''"
          @keydown.enter="add"
        >
        <input
          v-model="form.cap"
          class="input input--white cap-input mono"
          type="number"
          min="1"
          placeholder="Мест"
          title="Вместимость"
        >
        <div class="select-wrap type-sel">
          <select v-model="form.type">
            <option v-for="t in ROOM_TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
          <span class="chev">▾</span>
        </div>
        <button class="btn-primary" @click="add">＋ Добавить</button>
      </div>
      <div v-if="form.err" class="form-err"><span>⚠</span><span>{{ form.err }}</span></div>
    </div>

    <div class="table">
      <div class="thead">
        <span>АУДИТОРИЯ</span><span class="right">МЕСТ</span><span>ТИП</span><span>ЗАНЯТОСТЬ</span><span></span>
      </div>
      <div v-for="r in rows" :key="r.id" class="trow">
        <span class="rid">{{ r.id }}</span>
        <span class="cap mono right">{{ r.capacity }}</span>
        <span class="rtype">{{ r.type }}</span>
        <span class="rusage" :class="{ free: !r.used }">{{ r.usageLabel }}</span>
        <button
          class="del"
          :class="{ off: r.used }"
          :title="r.delTip"
          @click="del(r)"
        >✕</button>
      </div>
    </div>

    <div class="hint">
      Новая аудитория сразу доступна в диалоге размещения и учитывается генератором «Расписания».
      Удалить можно только аудиторию без назначенных пар.
    </div>
  </div>
</template>

<style scoped>
.rooms { display: flex; flex-direction: column; min-height: 0; flex: 1; }
.new-room {
  flex: none;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: var(--hover);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.new-row { display: flex; gap: 8px; align-items: center; }
.id-input { flex: none; width: 130px; font-size: 12.5px; }
.cap-input { flex: none; width: 74px; font: 500 12.5px var(--mono); text-align: right; }
.type-sel { flex: 1; }

.table { flex: 1; overflow-y: auto; padding: 10px 18px 14px; }
.thead, .trow {
  display: grid;
  grid-template-columns: 110px 64px 1fr 130px 30px;
  gap: 6px;
  align-items: center;
}
.thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.trow { padding: 7px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.right { text-align: right; }
.rid { font-size: 12.5px; font-weight: 600; }
.cap { font-size: 12px; color: var(--sub); }
.rtype { font-size: 12px; color: var(--sub); }
.rusage { font-size: 11.5px; color: var(--sub); }
.rusage.free { color: var(--faint); }
.del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 6px; border-radius: 5px; }
.del.off { color: #C9C5BB; cursor: not-allowed; }

.hint {
  flex: none;
  padding: 11px 18px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 11px;
  color: var(--muted);
  line-height: 1.5;
}
</style>
