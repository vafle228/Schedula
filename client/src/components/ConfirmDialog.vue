<script setup>
import { watch, onBeforeUnmount } from 'vue'
import { useConfirmDialog } from '../composables/useConfirm.js'

const { state, confirm, cancel } = useConfirmDialog()

function onKey(e) {
  if (e.key === 'Escape') { e.preventDefault(); cancel() }
  else if (e.key === 'Enter') { e.preventDefault(); confirm() }
}

watch(() => state.open, (open) => {
  if (open) document.addEventListener('keydown', onKey)
  else document.removeEventListener('keydown', onKey)
})
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div v-if="state.open" class="cfd-overlay" @click="cancel">
    <div class="cfd-card" @click.stop>
      <div class="cfd-head">
        <span class="cfd-badge">!</span>
        <div class="cfd-text">
          <span class="cfd-title">{{ state.title }}</span>
          <span class="cfd-message">{{ state.message }}</span>
        </div>
      </div>
      <div v-if="state.entityName" class="cfd-entity mono" :title="state.entityName">
        {{ state.entityName }}
      </div>
      <div class="cfd-foot">
        <span class="cfd-spacer"></span>
        <button class="cfd-cancel" @click="cancel">{{ state.cancelLabel }}</button>
        <button class="cfd-confirm" @click="confirm">{{ state.confirmLabel }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes cfdIn {
  from { opacity: 0; transform: translateY(6px) scale(0.99); }
  to { opacity: 1; transform: none; }
}

.cfd-overlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(31, 30, 27, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--sans);
}
.cfd-card {
  width: 440px;
  max-width: calc(92vw / 1.15);
  background: var(--panel);
  border-radius: var(--r-2xl);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
  overflow: hidden;
  animation: cfdIn 0.14s ease-out;
}

.cfd-head { display: flex; gap: 14px; padding: 20px 20px 12px; }
.cfd-badge {
  flex: none;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(194, 69, 54, 0.1);
  color: var(--red);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  font-weight: 700;
}
.cfd-text { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 0; }
.cfd-title { font-size: 15.5px; font-weight: 600; color: var(--fg); }
.cfd-message { font-size: 12.5px; color: var(--muted); line-height: 1.5; }

.cfd-entity {
  margin: 2px 20px 4px 72px;
  padding: 9px 12px;
  background: var(--chip, #f6f5f2);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--r-lg);
  font-weight: 500;
  font-size: 12.5px;
  color: var(--fg);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cfd-foot { display: flex; align-items: center; gap: 8px; padding: 14px 20px 18px; }
.cfd-spacer { flex: 1; }
.cfd-cancel,
.cfd-confirm {
  font-family: var(--sans);
  font-size: 13px;
  border-radius: var(--r-lg);
  cursor: pointer;
}
.cfd-cancel {
  border: 1px solid rgba(0, 0, 0, 0.16);
  background: var(--panel);
  color: #3a382f;
  font-weight: 500;
  padding: 8px 16px;
}
.cfd-cancel:hover { background: #fbfaf8; }
.cfd-confirm {
  border: none;
  background: var(--red);
  color: #fff;
  font-weight: 600;
  padding: 8px 18px;
}
.cfd-confirm:hover { background: #a5392c; }
</style>
