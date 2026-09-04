<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps<{
  x: number
  y: number
  visible: boolean
  type: 'series' | 'volume' | null
  isFavorite?: boolean
}>()

const emit = defineEmits<{
  edit: []
  delete: []
  addVolume: []
  addSeries: []
  close: []
  favorite: []
}>()

const menuRef = ref<HTMLElement | null>(null)

function handleGlobalClick(e: MouseEvent) {
  if (props.visible && menuRef.value && !menuRef.value.contains(e.target as Node)) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('click', handleGlobalClick))
onUnmounted(() => window.removeEventListener('click', handleGlobalClick))
</script>

<template>
  <div
    v-if="visible"
    ref="menuRef"
    :style="{ top: `${y}px`, left: `${x}px` }"
    class="context-menu"
  >
    <div v-if="type === null"     class="menu-item" @click.stop="emit('addSeries')">Add Series</div>
    <div v-if="type === 'series'" class="menu-item" @click.stop="emit('addVolume')">Add Volume</div>
    <div v-if="type !== null"     class="menu-item" @click.stop="emit('favorite')">
      <span class="icon icon-star menu-item-icon" :class="{ 'menu-star-active': isFavorite }" />
      {{ isFavorite ? 'Unfavorite' : 'Favorite' }}
    </div>
    <div v-if="type !== null"     class="menu-item" @click.stop="emit('edit')">Edit</div>
    <div v-if="type !== null"     class="menu-item" @click.stop="emit('delete')">Delete</div>
  </div>
</template>