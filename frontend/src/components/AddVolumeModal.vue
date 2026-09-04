<script setup lang="ts">
import { ref, watch } from 'vue'

const API_URL = import.meta.env.VITE_API_URL

const props = defineProps<{ visible: boolean; seriesId: number | null }>()
const emit = defineEmits<{ close: []; added: [] }>()

const volumeNumber = ref('')
const coverFile = ref<File | null>(null)
const preview = ref<string | null>(null)
const error = ref('')

watch(() => props.visible, (v) => {
  if (v) { volumeNumber.value = ''; coverFile.value = null; preview.value = null; error.value = '' }
})

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    coverFile.value = input.files[0]
    preview.value = URL.createObjectURL(input.files[0])
  }
}

async function handleSubmit() {
  if (!volumeNumber.value) { error.value = 'Volume number is required'; return }
  const res = await fetch(
    `${API_URL}/volumes/?series_id=${props.seriesId}&volume_number=${volumeNumber.value}&cover_url=`,
    { method: 'POST' }
  )
  if (!res.ok) { error.value = 'Something went wrong'; return }
  const volume = await res.json()
  if (coverFile.value) {
    const formData = new FormData()
    formData.append('file', coverFile.value)
    const uploadRes = await fetch(`${API_URL}/volumes/${volume.id}/cover`, { method: 'POST', body: formData })
    if (!uploadRes.ok) { error.value = 'Volume saved but cover upload failed'; return }
  }
  emit('added')
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="manga-modal-overlay" @click.self="emit('close')">
      <div class="manga-modal">
        <h1 class="manga-modal-title">Add Volume</h1>
        <input v-model="volumeNumber" placeholder="Volume number" type="number" class="manga-input" @keyup.enter="handleSubmit" />
        <div class="manga-file-row">
          <label class="manga-file-label">
            {{ coverFile ? coverFile.name : 'Choose cover image…' }}
            <input type="file" accept="image/*" class="manga-file-input" @change="handleFileChange" />
          </label>
        </div>
        <img v-if="preview" :src="preview" class="manga-preview" />
        <p v-if="error" class="manga-error">{{ error }}</p>
        <div class="manga-modal-actions">
          <button @click="handleSubmit" class="manga-btn manga-btn-ok">Add Volume</button>
          <button @click="emit('close')" class="manga-btn manga-btn-cancel">Cancel</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>