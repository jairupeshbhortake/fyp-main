<template>
  <div class="flight-list">
    <div class="list-header">
      <span class="list-count">{{ flights.length }} MISSIONS</span>
      <label class="upload-btn">
        + IMPORT
        <input type="file" accept=".txt,.csv" @change="handleUpload" hidden />
      </label>
    </div>

    <LoadingSpinner v-if="loading" label="Loading missions..." />

    <div v-else-if="flights.length === 0" class="empty">
      <span>NO MISSIONS FOUND</span>
      <p>Import a DJI .txt or Litchi .csv log file to begin.</p>
    </div>

    <div v-else class="list-items">
      <div
        v-for="f in flights"
        :key="f.id"
        class="flight-row"
        :class="{ active: selectedId === f.id }"
        @click="$emit('select', f)"
      >
        <div class="row-top">
          <span class="mission-id">{{ f.mission_id }}</span>
          <span class="source-badge" :class="f.source.toLowerCase()">{{ f.source }}</span>
        </div>
        <div class="row-meta">
          {{ formatDate(f.date) }} &bull;
          {{ formatDuration(f.duration_sec) }} &bull;
          {{ f.distance_km.toFixed(1) }} km &bull;
          {{ f.max_alt_m }}m ASL
        </div>
        <div class="row-tags">
          <span
            v-for="tag in f.tags"
            :key="tag.label"
            class="tag"
            :class="`tag-${tag.kind}`"
          >{{ tag.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStore } from 'vuex'
import { computed } from 'vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import { formatDate, formatDuration } from '../../utils/helpers'

defineProps({ selectedId: { type: Number, default: null } })
defineEmits(['select'])

const store = useStore()
const flights  = computed(() => store.getters['flights/filteredFlights'] || [])
const loading  = computed(() => store.state.flights.loading)

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  await store.dispatch('flights/upload', file)
  e.target.value = ''
}
</script>

<style scoped>
.flight-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.02);
}

.list-count { 
  font-family: var(--font-display);
  font-size: 13px; 
  font-weight: 600;
  letter-spacing: 1px; 
  color: var(--text-dim); 
}

.upload-btn {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  padding: 6px 14px;
  border: none;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: white;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
}

.upload-btn:hover { 
  filter: brightness(1.1);
  box-shadow: 0 6px 20px rgba(79, 172, 254, 0.5);
  transform: translateY(-1px);
}

.empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-faint);
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
}

.empty p { 
  font-family: var(--font-body);
  font-size: 12px; 
  margin-top: 12px; 
  color: var(--text-dim); 
  font-weight: 400;
}

.list-items { overflow-y: auto; flex: 1; padding: 8px; }

.flight-row {
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.flight-row:hover  { 
  background: rgba(255,255,255,0.05); 
  border-color: rgba(255,255,255,0.1);
  transform: translateX(4px);
}
.flight-row.active { 
  background: rgba(0, 242, 254, 0.08); 
  border-color: var(--accent-cyan);
}

.row-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }

.mission-id {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--text-main);
}

.source-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 12px;
  letter-spacing: 1px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--text-dim);
}

.source-badge.litchi { background: rgba(52, 211, 153, 0.15); border-color: rgba(52, 211, 153, 0.3); color: #34d399; }
.source-badge.dji    { background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); color: #fbbf24; }
.source-badge.manual { background: rgba(129, 140, 248, 0.15); border-color: rgba(129, 140, 248, 0.3); color: #818cf8; }

.row-meta { 
  font-family: var(--font-body);
  font-size: 11px; 
  color: var(--text-dim); 
  line-height: 1.6; 
}
.row-tags { margin-top: 6px; }
</style>
