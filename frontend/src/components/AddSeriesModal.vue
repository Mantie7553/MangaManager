<script setup lang="ts">
import { ref, watch } from 'vue'

const API_URL = import.meta.env.VITE_API_URL

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  close: []
  added: [series: { id: number; name: string; total_volumes: number | null; is_favorite: boolean; volumes: [] }]
}>()

const name = ref('')
const total_volumes = ref<number | null>(null)
const error = ref('')

watch(() => props.visible, (v) => {
  if (v) { name.value = ''; total_volumes.value = null; error.value = '' }
})

async function handleSubmit() {
  if (!name.value.trim()) { error.value = 'Name is required'; return }
  const totalParam = total_volumes.value != null ? `&total_volumes=${total_volumes.value}` : ''
  const res = await fetch(`${API_URL}/series/?name=${encodeURIComponent(name.value)}${totalParam}`, { method: 'POST' })
  if (res.status === 409) { error.value = 'Series already exists'; return }
  if (!res.ok)            { error.value = 'Something went wrong';   return }
  const series = await res.json()
  emit('added', { ...series, total_volumes: series.total_volumes ?? null, is_favorite: series.is_favorite ?? false, volumes: [] })
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="manga-modal-overlay" @click.self="emit('close')">
      <div class="manga-modal">
        <h1 class="manga-modal-title">Add Series</h1>
        <input v-model="name" placeholder="Title" class="manga-input" @keyup.enter="handleSubmit" />
        <input v-model.number="total_volumes" type="number" min="1" placeholder="Total volumes (optional)" class="manga-input" @keyup.enter="handleSubmit" />
        <p v-if="error" class="manga-error">{{ error }}</p>
        <div class="manga-modal-actions">
          <button @click="handleSubmit" class="manga-btn manga-btn-ok">Add Series</button>
          <button @click="emit('close')" class="manga-btn manga-btn-cancel">Cancel</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>