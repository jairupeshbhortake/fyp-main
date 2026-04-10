<template>
  <div class="btt-wrap">
    <div class="btt-header">
      <span class="btt-title">Battery % vs Flight</span>
      <div class="btt-legend">
        <span class="leg"><span class="swatch sw-start" />Start %</span>
        <span class="leg"><span class="swatch sw-end" />End %</span>
        <span class="leg"><span class="swatch sw-drop" />Drain</span>
      </div>
    </div>

    <div v-if="chartData.length === 0" class="btt-empty">
      No battery data available – import flight logs with battery telemetry.
    </div>

    <div v-else class="btt-body" ref="chartRef">
      <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none" class="btt-svg">
        <defs>
          <!-- Start % gradient -->
          <linearGradient id="grad-start" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.02"/>
          </linearGradient>
          <!-- End % gradient -->
          <linearGradient id="grad-end" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#4ade80" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#4ade80" stop-opacity="0.02"/>
          </linearGradient>
        </defs>

        <!-- Grid lines -->
        <line v-for="y in gridYs" :key="'gy'+y"
          :x1="PAD_L" :y1="y" :x2="W - PAD_R" :y2="y"
          stroke="rgba(255,255,255,0.05)" stroke-width="1"/>

        <!-- Grid labels -->
        <text v-for="(pct, i) in [0,25,50,75,100]" :key="'gl'+i"
          :x="PAD_L - 6" :y="yScale(pct) + 4"
          text-anchor="end" font-size="9" fill="rgba(255,255,255,0.3)">
          {{ pct }}%
        </text>

        <!-- Start fill -->
        <polygon :points="fillPoints(startPoints)" fill="url(#grad-start)" />
        <!-- End fill -->
        <polygon :points="fillPoints(endPoints)" fill="url(#grad-end)" />

        <!-- Drain area (between start and end) -->
        <polygon :points="drainPoints" fill="rgba(239,68,68,0.08)" />

        <!-- Start line -->
        <polyline
          :points="pointsStr(startPoints)"
          fill="none" stroke="#f59e0b" stroke-width="1.8"
          stroke-linejoin="round" stroke-linecap="round"/>

        <!-- End line -->
        <polyline
          :points="pointsStr(endPoints)"
          fill="none" stroke="#4ade80" stroke-width="1.8"
          stroke-linejoin="round" stroke-linecap="round"/>

        <!-- Dots – Start -->
        <circle v-for="p in startPoints" :key="'ds'+p.x"
          :cx="p.x" :cy="p.y" r="3"
          fill="#f59e0b" stroke="#1a1d2e" stroke-width="1.5">
          <title>{{ p.label }}\nStart: {{ p.val }}%</title>
        </circle>

        <!-- Dots – End -->
        <circle v-for="p in endPoints" :key="'de'+p.x"
          :cx="p.x" :cy="p.y" r="3"
          fill="#4ade80" stroke="#1a1d2e" stroke-width="1.5">
          <title>{{ p.label }}\nEnd: {{ p.val }}%</title>
        </circle>

        <!-- X-axis labels -->
        <text v-for="p in labelPoints" :key="'xl'+p.x"
          :x="p.x" :y="H - 4"
          text-anchor="middle" font-size="8" fill="rgba(255,255,255,0.3)">
          {{ p.label }}
        </text>
      </svg>
    </div>

    <!-- battery health cards row -->
    <div v-if="batteries.length" class="batt-cards">
      <div
        v-for="b in batteries"
        :key="b.serial"
        class="batt-card"
        :class="healthClass(b.health_pct)"
      >
        <div class="bc-top">
          <span class="bc-serial">{{ b.serial }}</span>
          <span class="bc-badge" :class="healthClass(b.health_pct)">
            {{ b.health_pct.toFixed(0) }}%
          </span>
        </div>
        <div class="bc-bar-track">
          <div class="bc-bar-fill" :class="healthClass(b.health_pct)"
            :style="{ width: b.health_pct + '%' }" />
        </div>
        <div class="bc-stats">
          <div class="bc-stat"><span class="bcs-l">Cycles</span><span class="bcs-v">{{ b.cycle_count }}</span></div>
          <div class="bc-stat"><span class="bcs-l">Avg End</span><span class="bcs-v">{{ b.avg_end_pct.toFixed(0) }}%</span></div>
          <div class="bc-stat"><span class="bcs-l">Flights</span><span class="bcs-v">{{ b.flights_count }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const chartRef = ref(null)

/* ── layout constants ── */
const W     = 800
const H     = 200
const PAD_L = 36
const PAD_R = 12
const PAD_T = 12
const PAD_B = 20

/* ── data ── */
const flights  = computed(() => (store.getters['flights/filteredFlights'] || []).slice(0, 30))
const batteries = computed(() => store.state.analytics.batteryHealth || [])

const chartData = computed(() =>
  flights.value.filter(f => f.batt_start_pct != null || f.batt_end_pct != null)
)

/* ── scaling ── */
function yScale(pct) {
  return PAD_T + (1 - pct / 100) * (H - PAD_T - PAD_B)
}

function xScale(i) {
  const n = chartData.value.length
  if (n <= 1) return (W - PAD_L - PAD_R) / 2 + PAD_L
  return PAD_L + (i / (n - 1)) * (W - PAD_L - PAD_R)
}

/* ── points ── */
const startPoints = computed(() =>
  chartData.value.map((f, i) => ({
    x: xScale(i),
    y: yScale(f.batt_start_pct ?? 100),
    val: f.batt_start_pct ?? 100,
    label: f.mission_id,
  }))
)

const endPoints = computed(() =>
  chartData.value.map((f, i) => ({
    x: xScale(i),
    y: yScale(f.batt_end_pct ?? 0),
    val: f.batt_end_pct ?? 0,
    label: f.mission_id,
  }))
)

/* ── label decimation ── */
const labelPoints = computed(() => {
  const all = startPoints.value
  if (all.length <= 10) return all.map(p => ({ x: p.x, label: p.label.slice(-3) }))
  const step = Math.ceil(all.length / 8)
  return all.filter((_, i) => i % step === 0 || i === all.length - 1)
    .map(p => ({ x: p.x, label: p.label.slice(-3) }))
})

/* ── helper: "start, filled down to bottom" polygon ── */
function fillPoints(pts) {
  if (!pts.length) return ''
  const bottom = H - PAD_B
  const first  = pts[0]
  const last   = pts[pts.length - 1]
  return [
    ...pts.map(p => `${p.x},${p.y}`),
    `${last.x},${bottom}`,
    `${first.x},${bottom}`,
  ].join(' ')
}

/* ── drain polygon (between start and end lines) ── */
const drainPoints = computed(() => {
  const s = startPoints.value
  const e = endPoints.value
  if (!s.length) return ''
  return [
    ...s.map(p => `${p.x},${p.y}`),
    ...[...e].reverse().map(p => `${p.x},${p.y}`),
  ].join(' ')
})

function pointsStr(pts) {
  return pts.map(p => `${p.x},${p.y}`).join(' ')
}

/* ── grid ── */
const gridYs = computed(() => [0, 25, 50, 75, 100].map(yScale))

/* ── health util ── */
function healthClass(pct) {
  if (pct >= 90) return 'good'
  if (pct >= 80) return 'ok'
  if (pct >= 70) return 'warn'
  return 'bad'
}
</script>

<style scoped>
.btt-wrap {
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}

.btt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid var(--glass-border);
}

.btt-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.btt-legend { display: flex; gap: 16px; }

.leg {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: var(--text-faint);
}

.swatch { width: 10px; height: 10px; border-radius: 50%; }
.sw-start { background: #f59e0b; }
.sw-end   { background: #4ade80; }
.sw-drop  { background: rgba(239,68,68,0.5); }

.btt-empty {
  padding: 40px 24px;
  text-align: center;
  font-size: 12px;
  color: var(--text-faint);
  letter-spacing: 0.3px;
}

.btt-body {
  padding: 8px 12px 4px;
}

.btt-svg {
  width: 100%;
  height: 200px;
  display: block;
}

/* Battery health cards */
.batt-cards {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding: 14px 16px;
  border-top: 1px solid var(--glass-border);
  background: rgba(0,0,0,0.1);
}

.batt-card {
  flex: 1;
  min-width: 160px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.2s;
}

.batt-card.good { border-color: rgba(34,197,94,0.3); }
.batt-card.ok   { border-color: rgba(245,158,11,0.3); }
.batt-card.warn { border-color: rgba(251,191,36,0.4); }
.batt-card.bad  { border-color: rgba(239,68,68,0.4); }

.bc-top { display: flex; justify-content: space-between; align-items: center; }

.bc-serial {
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 1px;
  color: #f59e0b;
}

.bc-badge {
  font-size: 9px;
  letter-spacing: 1px;
  padding: 2px 7px;
  border: 1px solid;
  border-radius: 2px;
}

.bc-badge.good { border-color: rgba(34,197,94,0.5);  color: #4ade80; }
.bc-badge.ok   { border-color: rgba(245,158,11,0.5); color: #f59e0b; }
.bc-badge.warn { border-color: rgba(251,191,36,0.5); color: #fbbf24; }
.bc-badge.bad  { border-color: rgba(239,68,68,0.5);  color: #f87171; }

.bc-bar-track {
  height: 3px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}

.bc-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s;
}

.bc-bar-fill.good { background: #22c55e; }
.bc-bar-fill.ok   { background: #f59e0b; }
.bc-bar-fill.warn { background: #fbbf24; }
.bc-bar-fill.bad  { background: #ef4444; }

.bc-stats { display: flex; gap: 10px; }

.bcs-l { display: block; font-size: 8px; letter-spacing: 1px; color: var(--text-faint); text-transform: uppercase; margin-bottom: 2px; }
.bcs-v { display: block; font-family: var(--font-display); font-size: 14px; color: #f59e0b; }
</style>
