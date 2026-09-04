<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import ContextMenu from '../components/ContextMenu.vue'
import EditModal from '../components/EditModal.vue'
import AddSeriesModal from '../components/AddSeriesModal.vue'
import AddVolumeModal from '../components/AddVolumeModal.vue'
import Toolbar from '../components/Toolbar.vue'


const API_URL = import.meta.env.VITE_API_URL

interface Volume {
  id: number
  volume_number: number
  cover_url: string | null
  is_favorite: boolean
}

interface Series {
  id: number
  name: string
  total_volumes: number | null
  is_favorite: boolean
  volumes: Volume[]
}

const series = ref<Series[]>([])

// ── Sort state ─────────────────────────────────────────────────────────────
type SeriesSort = 'name-asc' | 'name-desc' | 'none' | 'fav-first'
type VolumeSort = 'vol-asc' | 'vol-desc' | 'fav-first'

const seriesSort = ref<SeriesSort>((localStorage.getItem('seriesSort') as SeriesSort) ?? 'none')
const volumeSort = ref<VolumeSort>((localStorage.getItem('volumeSort') as VolumeSort) ?? 'vol-asc')
const search = ref('')

watch(seriesSort, val => localStorage.setItem('seriesSort', val))
watch(volumeSort, val => localStorage.setItem('volumeSort', val))

const sortedSeries = computed(() => {
  const q = search.value.trim().toLowerCase()
  let result = [...series.value]

  // Filter by search query
  if (q) result = result.filter(s => s.name.toLowerCase().includes(q))

  // Sort
  if (seriesSort.value === 'name-asc') result.sort((a, b) => a.name.localeCompare(b.name))
    else if (seriesSort.value === 'name-desc') result.sort((a, b) => b.name.localeCompare(a.name))
    else if (seriesSort.value === 'fav-first') result.sort((a, b) => Number(b.is_favorite) - Number(a.is_favorite))

  return result.map(s => ({
    ...s,
    volumes: [...s.volumes].sort((a, b) => {
      if (volumeSort.value === 'vol-asc') return a.volume_number - b.volume_number
      if (volumeSort.value === 'vol-desc') return b.volume_number - a.volume_number
      return Number(b.is_favorite) - Number(a.is_favorite)
    })
  }))
})

// ── Context menu — global listener ─────────────────────────────────────────
const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const menuTarget = ref<{ type: 'series' | 'volume'; id: number; seriesId?: number } | null>(null)

function closeMenu() {
  menuVisible.value = false
  menuTarget.value = null
}

function handleGlobalContextMenu(e: MouseEvent) {
  // Walk up the DOM from the right-clicked element looking for a data-menu attribute
  let el = e.target as HTMLElement | null
  while (el) {
    const menuType = el.dataset.menuType
    if (menuType === 'series' || menuType === 'volume') {
      e.preventDefault()
      menuX.value = e.clientX
      menuY.value = e.clientY
      menuTarget.value = {
        type: menuType,
        id: Number(el.dataset.menuId),
        seriesId: el.dataset.menuSeriesId ? Number(el.dataset.menuSeriesId) : undefined
      }
      menuVisible.value = true
      return
    }
    el = el.parentElement
  }
  // Right-clicked on something with no data-menu — close any open menu
  closeMenu()
}

onMounted(async () => {
  window.addEventListener('contextmenu', handleGlobalContextMenu)
  const res = await fetch(`${API_URL}/series/`)
  series.value = await res.json()
})

onUnmounted(() => {
  window.removeEventListener('contextmenu', handleGlobalContextMenu)
})

// ── Missing volumes ────────────────────────────────────────────────────────
function missingVolumes(s: Series): number[] {
  if (s.volumes.length === 0) return []
  const owned = new Set(s.volumes.map(v => v.volume_number))
  const min = Math.min(...s.volumes.map(v => v.volume_number))
  const max = s.total_volumes ?? Math.max(...s.volumes.map(v => v.volume_number))
  const missing: number[] = []
  for (let i = min; i <= max; i++) {
    if (!owned.has(i)) missing.push(i)
  }
  return missing
}

function missingLabel(s: Series): string {
  const missing = missingVolumes(s)
  const cap = 5
  if (missing.length <= cap) return missing.join(', ')
  return missing.slice(0, cap).join(', ') + ` +${missing.length - cap} more`
}

const addSeriesVisible = ref(false)

function onSeriesAdded(newSeries: { id: number; name: string; total_volumes: number | null; is_favorite: boolean; volumes: [] }) {
  series.value.push(newSeries)
}

// ── Add Volume modal ───────────────────────────────────────────────────────
const addVolumeVisible = ref(false)
const addVolumeSeriesId = ref<number | null>(null)

function openAddVolume(seriesId: number) {
  addVolumeSeriesId.value = seriesId
  addVolumeVisible.value = true
  closeMenu()
}

async function onVolumeAdded() {
  const res = await fetch(`${API_URL}/series/`)
  series.value = await res.json()
}

// ── Edit modal ─────────────────────────────────────────────────────────────
const editModalVisible = ref(false)
const editTarget = ref<{ type: 'series' | 'volume'; id: number; seriesId?: number } | null>(null)
const editCurrentName = ref('')
const editCurrentTotalVolumes = ref<number | null>(null)
const editCurrentVolumeNumber = ref(0)

async function handleDelete() {
  const target = menuTarget.value
  if (!target) return
  closeMenu()

  if (target.type === 'series') {
    await fetch(`${API_URL}/series/${target.id}`, { method: 'DELETE' })
    series.value = series.value.filter(s => s.id !== target.id)
  } else {
    await fetch(`${API_URL}/volumes/${target.seriesId}/${target.id}`, { method: 'DELETE' })
    const s = series.value.find(s => s.id === target.seriesId)
    if (s) s.volumes = s.volumes.filter(v => v.id !== target.id)
  }
}

async function handleFavorite() {
  const target = menuTarget.value
  if (!target) return
  closeMenu()

  if (target.type === 'series') {
    await fetch(`${API_URL}/series/${target.id}/favorite`, { method: 'PATCH' })
    const s = series.value.find(s => s.id === target.id)
    if (s) s.is_favorite = !s.is_favorite
  } else {
    await fetch(`${API_URL}/volumes/${target.id}/favorite`, { method: 'PATCH' })
    const s = series.value.find(s => s.id === target.seriesId)
    const vol = s?.volumes.find(v => v.id === target.id)
    if (vol) vol.is_favorite = !vol.is_favorite
  }
}

function handleEdit() {
  const target = menuTarget.value
  if (!target) return
  closeMenu()

  if (target.type === 'series') {
    const s = series.value.find(s => s.id === target.id)
    editCurrentName.value = s?.name ?? ''
    editCurrentTotalVolumes.value = s?.total_volumes ?? null
  } else {
    const s = series.value.find(s => s.id === target.seriesId)
    const vol = s?.volumes.find(v => v.id === target.id)
    editCurrentVolumeNumber.value = vol?.volume_number ?? 0
  }

  editTarget.value = target
  editModalVisible.value = true
}

async function handleSave(value: string | number, file: File | null, totalVolumes?: number | null) {
  const target = editTarget.value
  if (!target) return

  if (target.type === 'series') {
    const totalParam = totalVolumes != null ? `&total_volumes=${totalVolumes}` : ''
    await fetch(`${API_URL}/series/${target.id}?name=${encodeURIComponent(value as string)}${totalParam}`, { method: 'PUT' })
    const s = series.value.find(s => s.id === target.id)
    if (s) {
      s.name = value as string
      s.total_volumes = totalVolumes ?? null
    }
  } else {
    const s = series.value.find(s => s.id === target.seriesId)
    const vol = s?.volumes.find(v => v.id === target.id)
    const existingCoverUrl = vol?.cover_url ?? ''

    await fetch(
      `${API_URL}/volumes/${target.seriesId}/${target.id}?volume_number=${value}&cover_url=${encodeURIComponent(existingCoverUrl)}`,
      { method: 'PUT' }
    )

    if (file) {
      const formData = new FormData()
      formData.append('file', file)
      await fetch(`${API_URL}/volumes/${target.id}/cover`, { method: 'POST', body: formData })
    }

    if (vol) vol.volume_number = value as number
  }

  const res = await fetch(`${API_URL}/series/`)
  series.value = await res.json()

  editModalVisible.value = false
  editTarget.value = null
}
</script>

<template>
  <div class="page-wrapper">
    <div class="side-border" />

    <div class="page">

      <!-- toolbar -->
      <Toolbar
        v-model:seriesSort="seriesSort"
        v-model:volumeSort="volumeSort"
        v-model:search="search"
      />

      <!-- Shelves -->
      <div v-for="s in sortedSeries" :key="s.id" class="shelf-section">
        <div class="series-title-area">
          <h2 class="series-title" :data-menu-type="'series'" :data-menu-id="s.id">
            <span v-if="s.is_favorite" class="icon icon-star fav-star" />
            {{ s.name }}
            <span class="volume-count">{{ s.volumes.length }}{{ s.total_volumes != null ? ` / ${s.total_volumes}` : '' }}</span>
          </h2>
          <div v-if="missingVolumes(s).length" class="missing-note">
            <span class="missing-note-label">Missing</span>
            <span class="missing-note-vols">{{ missingLabel(s) }}</span>
          </div>
        </div>

        <div
          class="row"
          :data-menu-type="'series'"
          :data-menu-id="s.id"
        >
          <!-- Add volume button (left-click only, no menu) -->
           <div class="h-fit">
            <div v-if="s.total_volumes != s.volumes.length" class="volume" @click.stop="openAddVolume(s.id)">
              <div class="add-volume cover">+</div>
            </div>
           </div>

          <!-- Volume tiles -->
          <div v-for="vol in s.volumes" :key="vol.id" class="h-fit">
            <div
              class="volume"
              :data-menu-type="'volume'"
              :data-menu-id="vol.id"
              :data-menu-series-id="s.id"
            >
              <span v-if="vol.is_favorite" class="icon icon-star vol-fav-star" />
              <img
                v-if="vol.cover_url"
                :src="`${API_URL}${vol.cover_url}`"
                class="cover"
                :data-menu-type="'volume'"
                :data-menu-id="vol.id"
                :data-menu-series-id="s.id"
              />
              <div
                v-else
                class="volume-title"
                :data-menu-type="'volume'"
                :data-menu-id="vol.id"
                :data-menu-series-id="s.id"
              >
                <span class="vol-placeholder-label">Vol</span>
                <span class="vol-placeholder-num">{{ vol.volume_number }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="shelf-floor" />
      </div>

      <!-- Add Series -->
      <div class="add-series-btn" @click.stop="addSeriesVisible = true">
        + Add Series
      </div>

      <ContextMenu
        :x="menuX"
        :y="menuY"
        :visible="menuVisible"
        :type="menuTarget?.type ?? null"
        :is-favorite="menuTarget
          ? menuTarget.type === 'series'
            ? series.find(s => s.id === menuTarget!.id)?.is_favorite
            : series.find(s => s.id === menuTarget!.seriesId)?.volumes.find(v => v.id === menuTarget!.id)?.is_favorite
          : false"
        @edit="handleEdit"
        @delete="handleDelete"
        @favorite="handleFavorite"
        @add-volume="openAddVolume(menuTarget!.id)"
        @add-series="addSeriesVisible = true; closeMenu()"
        @close="closeMenu"
      />
    </div>

    <div class="side-border" />
  </div>

  <AddSeriesModal
    :visible="addSeriesVisible"
    @close="addSeriesVisible = false"
    @added="onSeriesAdded"
  />

  <AddVolumeModal
    :visible="addVolumeVisible"
    :series-id="addVolumeSeriesId"
    @close="addVolumeVisible = false"
    @added="onVolumeAdded"
  />

  <EditModal
    :visible="editModalVisible"
    :type="editTarget?.type ?? null"
    :current-name="editCurrentName"
    :current-volume-number="editCurrentVolumeNumber"
    :current-total-volumes="editCurrentTotalVolumes"
    :current-cover-url="editTarget?.type === 'volume' ? series.find(s => s.id === editTarget?.seriesId)?.volumes.find(v => v.id === editTarget?.id)?.cover_url : null"
    @save="handleSave"
    @close="editModalVisible = false"
  />
</template>