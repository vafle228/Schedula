<script setup>
defineProps({
  tip: { type: String, required: true },
  size: { type: Number, default: 16 },
})
</script>

<template>
  <span
    class="info-dot"
    :style="{ width: size + 'px', height: size + 'px' }"
    :title="tip"
  >i</span>
</template>

<style scoped>
.info-dot {
  flex: none;
  border: 1px solid var(--ghost);
  border-radius: 50%;
  color: var(--muted);
  font: italic 600 10px Georgia, serif;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: help;
}
.info-dot:hover { border-color: var(--muted); color: var(--sub); }
</style>
