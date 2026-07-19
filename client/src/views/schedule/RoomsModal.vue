<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import RoomsEditor from '../../components/RoomsEditor.vue'
import { ui } from './useSchedule.js'

const count = computed(() => store.state.rooms.length)
</script>

<template>
  <ModalWindow v-if="ui.rooms" :title="'Аудитории: ' + count" :width="580" @close="ui.rooms = false">
    <div class="wrap">
      <RoomsEditor />
    </div>
  </ModalWindow>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; min-height: 0; max-height: 72vh; }
</style>
