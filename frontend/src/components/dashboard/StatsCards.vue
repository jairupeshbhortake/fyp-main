<template>
  <div class="stats-cards">
    <div class="card" v-for="card in cards" :key="card.label">
      <div class="card-label">{{ card.label }}</div>
      <div class="card-value">
        {{ card.value }}<span class="card-unit">{{ card.unit }}</span>
      </div>
      <div class="card-sub" v-if="card.sub">{{ card.sub }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const stats = computed(() => store.state.analytics.overview)

const cards = computed(() => {
  if (!stats.value) return []
  const s = stats.value
  return [
    { label: 'Total Missions', value: s.total_flights,                        unit: '',     sub: 'all time' },
    { label: 'Flight Time',    value: s.total_duration_hr?.toFixed(1),        unit: 'hr',   sub: `avg ${s.avg_duration_min} min` },
    { label: 'Total Range',    value: s.total_distance_km?.toFixed(1),        unit: 'km',   sub: `avg ${s.avg_distance_km} km` },
    { label: 'Max Altitude',   value: s.max_alt_ever_m,                       unit: 'm',    sub: 'all time peak' },
    { label: 'Top Speed',      value: s.max_speed_ever_ms?.toFixed(1) ?? '—', unit: 'm/s',  sub: 'fastest logged' },
    { label: 'Drones Flown',   value: Object.keys(s.flights_by_drone || {}).length, unit: '', sub: 'unique models' },
    { label: 'Launch Sites',   value: (s.home_locations || []).length,        unit: '',     sub: 'unique locations' },
  ]
})
</script>

<style scoped>
.stats-cards {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}

.card {
  padding: 16px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  box-shadow: var(--glass-shadow);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.15);
}

.card-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.card-value {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--text-main), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

.card-unit {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-faint);
  margin-left: 4px;
}

.card-sub {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 8px;
}
</style>
