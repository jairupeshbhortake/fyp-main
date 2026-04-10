<template>
  <div class="lb-wrap">
    <div class="lb-title">{{ title }}</div>
    <div v-if="!items.length" class="lb-empty">No data yet</div>
    <div v-for="(item, i) in items" :key="item.id" class="lb-row">
      <span class="lb-rank">#{{ i + 1 }}</span>
      <div class="lb-info">
        <div class="lb-mission">{{ item.mission_id }}</div>
        <div class="lb-date">{{ formatDate(item.date) }}</div>
      </div>
      <div class="lb-metric">
        <span class="lb-val">{{ formatValue(item) }}</span>
        <span class="lb-unit">{{ unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title:  { type: String,  default: 'Top Flights' },
  items:  { type: Array,   default: () => [] },
  metric: { type: String,  default: 'duration' }, // 'duration' | 'distance'
  unit:   { type: String,  default: '' },
})

function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatValue(item) {
  if (props.metric === 'duration') {
    const s = item.duration_sec || 0
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}m ${sec}s`
  }
  return Number(item.distance_km || 0).toFixed(1)
}
</script>

<style scoped>
.lb-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 20px;
  height: 100%;
}

.lb-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--text-dim);
  margin-bottom: 10px;
}

.lb-empty {
  font-size: 12px;
  color: var(--text-faint);
  padding: 20px 0;
  text-align: center;
}

.lb-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  transition: background 0.2s;
  cursor: default;
}
.lb-row:hover { background: rgba(0,242,254,0.06); border-color: rgba(0,242,254,0.15); }

.lb-rank {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 800;
  color: var(--text-faint);
  min-width: 32px;
}
.lb-row:nth-child(2) .lb-rank { color: #00f2fe; }
.lb-row:nth-child(3) .lb-rank { color: #4facfe; }
.lb-row:nth-child(4) .lb-rank { color: #818cf8; }

.lb-info { flex: 1; min-width: 0; }

.lb-mission {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lb-date {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 2px;
}

.lb-metric { text-align: right; }

.lb-val {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 700;
  color: #00f2fe;
}

.lb-unit {
  font-size: 10px;
  color: var(--text-faint);
  margin-left: 3px;
}
</style>
