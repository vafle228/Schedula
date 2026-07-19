<script setup>
defineProps({
  title: { type: String, default: '' },
  width: { type: Number, default: 480 },
  /* 'center' — dialog, 'right' — side drawer */
  placement: { type: String, default: 'center' },
})
const emit = defineEmits(['close'])
</script>

<template>
  <div class="overlay" :class="'overlay--' + placement" @click="emit('close')">
    <div
      class="win"
      :class="'win--' + placement"
      :style="{ width: width + 'px' }"
      @click.stop
    >
      <div class="head">
        <slot name="title">
          <span class="head-title">{{ title }}</span>
        </slot>
        <span class="x-close" title="Закрыть (Esc)" @click="emit('close')">×</span>
      </div>
      <slot />
      <div v-if="$slots.footer" class="foot">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(31, 30, 27, 0.4);
  display: flex;
}
.overlay--center { align-items: center; justify-content: center; }
.overlay--right { justify-content: flex-end; background: rgba(31, 30, 27, 0.35); }

.win {
  max-width: 94vw;
  background: var(--panel);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.win--center {
  max-height: 90vh;
  border-radius: var(--r-2xl);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}
.win--right {
  height: 100%;
  box-shadow: -12px 0 32px rgba(0, 0, 0, 0.15);
}

.head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title { font-size: 15px; font-weight: 600; flex: 1; }

.foot {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}
</style>
