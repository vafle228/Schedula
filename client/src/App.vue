<script setup>
import AppSidebar from './components/AppSidebar.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
</script>

<template>
  <div class="app-root">
    <AppSidebar />
    <div class="app-main">
      <router-view />
    </div>
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.app-root {
  /* body has zoom:1.15, so 100vh renders 15% taller than the viewport and
     clips the bottom (hiding the settings button). Divide it back out. */
  height: calc(100vh / 1.15);
  display: flex;
  min-height: 0;
  overflow: hidden;
}
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}
</style>
