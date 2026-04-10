<template>
  <div class="battery-page">
    <div class="page-header">
      <span class="page-title">// BATTERY HEALTH</span>
      <span class="page-sub">Per-pack health tracking and cycle history</span>
    </div>

    <LoadingSpinner v-if="loading" label="Analysing battery data..." />

    <template v-else>
      <div class="battery-grid">
        <div
          v-for="b in batteries"
          :key="b.serial"
          class="battery-card"
          :class="healthClass(b.health_pct)"
        >
          <!-- Card header -->
          <div class="card-header">
            <span class="serial">{{ b.serial }}</span>
            <span class="health-badge" :class="healthClass(b.health_pct)">
              {{ b.health_pct.toFixed(0) }}% HEALTH
            </span>
          </div>

          <!-- Health bar -->
          <div class="health-bar-track">
            <div
              class="health-bar-fill"
              :class="healthClass(b.health_pct)"
              :style="{ width: b.health_pct + '%' }"
            />
          </div>

          <!-- Stats -->
          <div class="card-stats">
            <div class="stat">
              <div class="stat-label">CYCLES</div>
              <div class="stat-val">{{ b.cycle_count }}</div>
            </div>
            <div class="stat">
              <div class="stat-label">AVG END %</div>
              <div class="stat-val">{{ b.avg_end_pct.toFixed(0) }}%</div>
            </div>
            <div class="stat">
              <div class="stat-label">FLIGHTS</div>
              <div class="stat-val">{{ b.flights_count }}</div>
            </div>
          </div>

          <!-- Cell voltage visualiser (mock) -->
          <div class="cells">
            <div
              v-for="n in 4"
              :key="n"
              class="cell-vis"
            >
              <div class="cell-bar">
                <div
                  class="cell-fill"
                  :class="healthClass(b.health_pct)"
                  :style="{ height: (b.health_pct * 0.75 + Math.random() * 5).toFixed(0) + '%' }"
                />
              </div>
              <span class="cell-label">C{{ n }}</span>
            </div>
          </div>

          <div class="card-footer">
            SN: {{ b.serial }}
          </div>
        </div>
      </div>

      <div v-if="batteries.length === 0" class="empty-state">
        <span>// NO BATTERY DATA</span>
        <p>Import flight logs to populate battery health tracking.</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import api from '../utils/api'

const batteries = ref([])
const loading   = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/analytics/battery-health')
    batteries.value = data
  } catch {
    batteries.value = []
  } finally {
    loading.value = false
  }
})

function healthClass(pct) {
  if (pct >= 90) return 'good'
  if (pct >= 80) return 'ok'
  if (pct >= 70) return 'warn'
  return 'bad'
}
</script>

<style scoped>
.battery-page { padding: 0 0 40px; }

.page-header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.02);
}

.page-title { font-family: var(--font-display); font-size: 14px; letter-spacing: 3px; color: var(--accent-cyan); }
.page-sub   { font-size: 11px; color: var(--text-faint); }

.battery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  padding: 24px;
}

.battery-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.battery-card.good { border-color: rgba(34,197,94,0.3); }
.battery-card.ok   { border-color: rgba(245,158,11,0.3); }
.battery-card.warn { border-color: rgba(251,191,36,0.4); }
.battery-card.bad  { border-color: rgba(239,68,68,0.4); }

.card-header { display: flex; justify-content: space-between; align-items: center; }

.serial {
  font-family: var(--font-display);
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--accent-cyan);
}

.health-badge {
  font-size: 9px;
  letter-spacing: 1px;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 2px;
}

.health-badge.good { border-color: rgba(34,197,94,0.5); color: #4ade80; }
.health-badge.ok   { border-color: rgba(245,158,11,0.5); color: var(--yellow); }
.health-badge.warn { border-color: rgba(251,191,36,0.5); color: #fbbf24; }
.health-badge.bad  { border-color: rgba(239,68,68,0.5);  color: #f87171; }

.health-bar-track {
  height: 4px;
  background: rgba(245,158,11,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.health-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s;
}

.health-bar-fill.good { background: #22c55e; }
.health-bar-fill.ok   { background: var(--yellow); }
.health-bar-fill.warn { background: #fbbf24; }
.health-bar-fill.bad  { background: var(--red); }

.card-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.stat-label { font-size: 8px; letter-spacing: 2px; color: var(--text-faint); text-transform: uppercase; margin-bottom: 3px; }
.stat-val   { font-family: var(--font-display); font-size: 16px; color: var(--accent-cyan); }

.cells {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  height: 52px;
}

.cell-vis { display: flex; flex-direction: column; align-items: center; gap: 3px; flex: 1; }

.cell-bar {
  width: 14px;
  height: 40px;
  background: rgba(245,158,11,0.07);
  border: 1px solid var(--border);
  border-radius: 1px;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
}

.cell-fill {
  width: 100%;
  border-radius: 1px;
  transition: height 0.5s;
}

.cell-fill.good { background: #22c55e; }
.cell-fill.ok   { background: var(--amber); }
.cell-fill.warn { background: #fbbf24; }
.cell-fill.bad  { background: var(--red); }

.cell-label { font-size: 8px; color: var(--text-faint); }

.card-footer { font-size: 9px; color: var(--text-faint); letter-spacing: 0.5px; border-top: 1px solid var(--border); padding-top: 8px; }

.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: var(--text-faint);
  font-size: 12px;
  letter-spacing: 2px;
}

.empty-state p { font-size: 11px; margin-top: 10px; letter-spacing: 0; }
</style>
