<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

type SeriesSort = 'name-asc' | 'name-desc' | 'none' | 'fav-first'
type VolumeSort = 'vol-asc' | 'vol-desc' | 'fav-first'

const props = defineProps<{
  seriesSort: SeriesSort
  volumeSort: VolumeSort
  search: string
}>()

const emit = defineEmits<{
  (e: 'update:seriesSort', val: SeriesSort): void
  (e: 'update:volumeSort', val: VolumeSort): void
  (e: 'update:search', val: string): void
}>()

const drawerOpen = ref(false)

const toolbarVisible = ref(true)

let lastScrollY = 0

function onScroll() {
  const y = window.scrollY
  if (y <= 8) {
    toolbarVisible.value = true
  } else if (y < lastScrollY - 4) {
    toolbarVisible.value = true
  } else if (y > lastScrollY + 4) {
    toolbarVisible.value = false
  }
  lastScrollY = y
}

function onTap() {
  toolbarVisible.value = true
}

onMounted(() => {
  lastScrollY = window.scrollY
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('pointerdown', onTap)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('pointerdown', onTap)
})

function cycleSeriesSort() {
  const next: Record<SeriesSort, SeriesSort> = {
    none: 'name-asc',
    'name-asc': 'name-desc',
    'name-desc': 'fav-first',
    'fav-first': 'none',
  }
  emit('update:seriesSort', next[props.seriesSort])
}

function toggleVolumeSort() {
  const next: Record<VolumeSort, VolumeSort> = {
    'vol-asc': 'vol-desc',
    'vol-desc': 'fav-first',
    'fav-first': 'vol-asc',
  }
  emit('update:volumeSort', next[props.volumeSort])
}


function onInput(e: Event) {
  emit('update:search', (e.target as HTMLInputElement).value)
}

function clearSearch() {
  emit('update:search', '')
}

const seriesSortLabel = {
  none: '—',
  'name-asc': 'A → Z',
  'name-desc': 'Z → A',
  'fav-first': '★ Favs',
}
</script>

<template>
  <!-- ── Desktop toolbar (hidden on mobile) ──────────────────────── -->
  <div class="toolbar toolbar-desktop" :class="{ 'toolbar-hidden': !toolbarVisible }">
    <div class="search-wrapper">
      <span class="icon icon-search search-icon"/>
      <input
        class="search-input"
        type="text"
        placeholder="Search series…"
        :value="search"
        @input="onInput"
      />
      <button v-if="search" class="search-clear" @click="clearSearch">X</button>
    </div>

    <div class="toolbar-divider" />

    <button class="sort-btn" @click.stop="cycleSeriesSort">
      Series
      <span v-if="seriesSort === 'name-asc'">A → Z ↑</span>
      <span v-else-if="seriesSort === 'name-desc'">Z → A ↓</span>
      <span v-else-if="seriesSort === 'fav-first'">★ Favs</span>
      <span v-else>—</span>
    </button>

    <button class="sort-btn" @click.stop="toggleVolumeSort">
      Vol #
      <span v-if="volumeSort === 'vol-asc'">1 → 9 ↑</span>
      <span v-else-if="volumeSort === 'vol-desc'">9 → 1 ↓</span>
      <span v-else-if="volumeSort === 'fav-first'">★ Favs</span>
    </button>
  </div>

  <!-- ── Mobile toolbar (hidden on desktop) ──────────────────────── -->
  <div class="toolbar toolbar-mobile" :class="{ 'toolbar-hidden': !toolbarVisible }">
    <!-- Active filter chips (so user can see state at a glance) -->
    <div class="mobile-chips">
      <span v-if="search" class="mobile-chip">
         {{ search }}
        <button class="chip-clear" @click="clearSearch">✕</button>
      </span>
      <span v-if="seriesSort !== 'none'" class="mobile-chip">
        Series: {{ seriesSortLabel[seriesSort] }}
      </span>
      <span v-if="volumeSort !== 'vol-asc'" class="mobile-chip">
        Vol: 9 → 1
      </span>
    </div>

    <!-- Hamburger button -->
    <button class="hamburger-btn" @click.stop="drawerOpen = !drawerOpen" :class="{ open: drawerOpen }">
      <span /><span /><span />
    </button>
  </div>

  <!-- ── Mobile drawer ────────────────────────────────────────────── -->
  <Transition name="drawer">
    <div v-if="drawerOpen" class="mobile-drawer">
      <!-- Search -->
      <div class="drawer-section">
        <div class="drawer-label">Search</div>
        <div class="search-wrapper drawer-search">
          <span class="icon icon-search search-icon" />
          <input
            class="search-input"
            type="text"
            placeholder="Search series…"
            :value="search"
            @input="onInput"
            autofocus
          />
          <button v-if="search" class="search-clear" @click="clearSearch">✕</button>
        </div>
      </div>

      <!-- Sort -->
      <div class="drawer-section">
        <div class="drawer-label">Sort by Series</div>
        <div class="drawer-btn-row">
          <button
            v-for="opt in (['none', 'name-asc', 'name-desc', 'fav-first'] as SeriesSort[])"
            :key="opt"
            class="drawer-sort-btn"
            :class="{ active: seriesSort === opt }"
            @click.stop="emit('update:seriesSort', opt)"
          >
            {{ opt === 'none' ? 'Default' : opt === 'name-asc' ? 'A → Z' : opt === 'name-desc' ? 'Z → A' : '★ Favs first' }}
          </button>
        </div>
      </div>

      <div class="drawer-section">
        <div class="drawer-label">Sort by Volume</div>
        <div class="drawer-btn-row">
          <button
            class="drawer-sort-btn"
            :class="{ active: volumeSort === 'vol-asc' }"
            @click.stop="emit('update:volumeSort', 'vol-asc')"
          >1 → 9</button>
          <button
            class="drawer-sort-btn"
            :class="{ active: volumeSort === 'vol-desc' }"
            @click.stop="emit('update:volumeSort', 'vol-desc')"
          >9 → 1</button>
        </div>
      </div>

      <button class="drawer-done-btn" @click.stop="drawerOpen = false">Done</button>
    </div>
  </Transition>

  <!-- Backdrop -->
  <Transition name="fade">
    <div v-if="drawerOpen" class="drawer-backdrop" @click="drawerOpen = false" />
  </Transition>
</template>