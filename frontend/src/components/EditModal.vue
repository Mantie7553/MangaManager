<script setup lang="ts">
import { ref, watch } from 'vue'

const API_URL = import.meta.env.VITE_API_URL

const props = defineProps<{
  visible: boolean
  type: 'series' | 'volume' | null
  currentName?: string
  currentVolumeNumber?: number
  currentTotalVolumes?: number | null
  currentCoverUrl?: string | null
}>()

const emit = defineEmits<{
  save: [value: string | number, file: File | null, totalVolumes: number | null]
  close: []
}>()

const value = ref('')
const totalVolumes = ref<number | null>(null)
const coverFile = ref<File | null>(null)
const preview = ref<string | null>(null)
const overlayRef = ref<HTMLElement | null>(null)

watch(() => props.visible, (v) => {
  if (v) {
    value.value = props.type === 'series' ? props.currentName ?? '' : String(props.currentVolumeNumber ?? '')
    totalVolumes.value = props.currentTotalVolumes ?? null
    coverFile.value = null
    preview.value = null
  }
})

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    coverFile.value = input.files[0]
    preview.value = URL.createObjectURL(input.files[0])
  }
}

function handleOverlayClick(e: MouseEvent) {
  if (e.target === overlayRef.value) emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" ref="overlayRef" class="manga-modal-overlay" @click="handleOverlayClick">
      <div class="modal-hit-area" @click.stop>
        <div class="manga-modal">
          <h2 class="manga-modal-title">{{ type === 'series' ? 'Edit Series' : 'Edit Volume' }}</h2>
          <input
            v-model="value"
            :type="type === 'volume' ? 'number' : 'text'"
            :placeholder="type === 'series' ? 'Series name' : 'Volume number'"
            class="manga-input"
            @keyup.enter="emit('save', type === 'volume' ? Number(value) : value, coverFile, totalVolumes)"
          />
          <div v-if="type === 'series'" class="manga-field">
            <label class="manga-label">Total volumes (optional)</label>
            <input v-model.number="totalVolumes" type="number" min="1" placeholder="e.g. 12" class="manga-input" />
          </div>
          <div v-if="type === 'volume'" class="manga-field">
            <img v-if="preview" :src="preview" class="manga-preview" />
            <img v-else-if="currentCoverUrl" :src="`${API_URL}${currentCoverUrl}`" class="manga-preview" />
            <div class="manga-file-row">
              <label class="manga-file-label">
                {{ coverFile ? coverFile.name : 'Choose new cover…' }}
                <input type="file" accept="image/*" class="manga-file-input" @change="handleFileChange" />
              </label>
            </div>
          </div>
          <div class="manga-modal-actions">
            <button class="manga-btn manga-btn-ok" @click="emit('save', type === 'volume' ? Number(value) : value, coverFile, totalVolumes)">Save</button>
            <button class="manga-btn manga-btn-cancel" @click="emit('close')">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>