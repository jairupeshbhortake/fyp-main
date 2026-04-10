<template>
  <div class="battery-chart">
    <div class="chart-header">
      <span class="chart-title">// battery per flight</span>
    </div>
    <div class="bars">
      <div
        v-for="item in barData"
        :key="item.id"
        class="bar-col"
        :title="`${item.label}\nStart: ${item.start}%  End: ${item.end}%`"
      >
        <div class="bar-track">
          <div class="bar-fill start" :style="{ height: item.start + '%' }" />
          <div class="bar-fill end" :style="{ height: item.end + '%', background: item.endColor }" />
        </div>
        <div class="bar-label">{{ item.shortId }}</div>
      </div>
    </div>
    <div class="legend">
      <span class="leg-item"><span class="swatch start-sw"/>Start %</span>
      <span class="leg-item"><span class="swatch end-sw"/>End %</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const flights = computed(() => (store.getters['flights/filteredFlights'] || []).slice(0, 20))

const barData = computed(() =>
  flights.value.map(f => ({
    id: f.id,
    label: f.mission_id,
    shortId: f.mission_id.slice(-3),
    start: f.batt_start_pct ?? 100,
    end:   f.batt_end_pct   ?? 0,
    endColor: (f.batt_end_pct ?? 50) < 20
      ? '#ef4444'
      : (f.batt_end_pct ?? 50) < 35
      ? '#fbbf24'
      : '#22c55e',
  }))
)
</script>

<style scoped>
.battery-chart {
  border: 1px solid var(--border);
  border-radius: 2px;
  background: var(--bg-card);
  overflow: hidden;
}

.chart-header { padding: 10px 14px 6px; border-bottom: 1px solid var(--border); }
.chart-title { font-size: 10px; letter-spacing: 2px; color: var(--text-dim); text-transform: uppercase; }

.bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  padding: 12px 14px 4px;
  height: 140px;
  overflow-x: auto;
}

.bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.bar-track {
  width: 16px;
  height: 110px;
  background: rgba(245,158,11,0.06);
  border: 1px solid var(--border);
  border-radius: 1px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.bar-fill {
  width: 100%;
  position: absolute;
  bottom: 0;
  border-radius: 1px;
  transition: height 0.4s;
}

.bar-fill.start { background: rgba(245,158,11,0.2); }
.bar-fill.end   { background: #22c55e; }

.bar-label { font-size: 8px; color: var(--text-faint); letter-spacing: 0.5px; }

.legend {
  display: flex;
  gap: 16px;
  padding: 6px 14px 10px;
  border-top: 1px solid var(--border);
}

.leg-item { display: flex; align-items: center; gap: 5px; font-size: 10px; color: var(--text-dim); }
.swatch { width: 10px; height: 10px; border-radius: 1px; }
.start-sw { background: rgba(245,158,11,0.3); }
.end-sw   { background: #22c55e; }
</style>
