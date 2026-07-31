<script setup>
/**
 * Круглый аватар преподавателя: фото с сервера, иначе инициалы.
 *
 * Фото приходит в поле `photo` готовым data-URL (сервер хранит base64 JPEG и
 * подставляет префикс при выдаче), поэтому здесь достаточно фона.
 */
import { computed } from 'vue'
import { initials, avatarBg } from '../utils/format.js'

const props = defineProps({
  teacher: { type: Object, default: null },
  size: { type: Number, default: 26 },
  /** Заливка вместо фото — например, подсветка перегруза по норме часов. */
  accent: { type: String, default: '' },
  /** Показывать ФИО во всплывающей подсказке. */
  tip: { type: Boolean, default: true },
})

const photo = computed(() => (props.teacher ? props.teacher.photo : null))
const shows = computed(() => !!photo.value && !props.accent)
const label = computed(() => (shows.value ? '' : initials(props.teacher && props.teacher.name)))

const style = computed(() => ({
  width: props.size + 'px',
  height: props.size + 'px',
  fontSize: Math.max(9, Math.round(props.size * 0.38)) + 'px',
  background: props.accent || avatarBg(photo.value),
  color: props.accent ? '#FFFFFF' : '#5C574E',
}))
</script>

<template>
  <span class="t-avatar" :style="style" :title="tip && teacher ? teacher.name : null">{{ label }}</span>
</template>

<style scoped>
.t-avatar {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 600;
  line-height: 1;
  overflow: hidden;
  user-select: none;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background-size: cover !important;
  background-position: center !important;
}
</style>
