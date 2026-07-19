<script setup>
import AppSidebar from './components/AppSidebar.vue'
</script>

<template>
  <div class="app-root">
    <AppSidebar />
    <div class="app-main">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.app-root {
  height: 100vh;
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
