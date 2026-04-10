<template>
  <div class="flight-detail">
    <LoadingSpinner v-if="loading" label="Loading mission data..." />

    <template v-else-if="flight">
      <!-- Page header -->
      <div class="detail-header">
        <button class="back-btn" @click="$router.back()">← BACK</button>
        <div class="header-center">
          <span class="mission-id">{{ flight.mission_id }}</span>
          <span class="source-badge" :class="flight.source.toLowerCase()">{{ flight.source }}</span>
        </div>
        <div class="header-actions">
          <button class="btn" @click="toggleReplay">{{ replaying ? '⏹ STOP' : '▶ REPLAY' }}</button>
          <button class="btn" @click="doExport('csv')">CSV</button>
          <button class="btn" @click="doExport('gpx')">GPX</button>
          <button class="btn" @click="doExport('kml')">KML</button>
          <button class="btn danger" @click="confirmDelete">DELETE</button>
        </div>
      </div>

      <!-- Stat strip -->
      <div class="stats-strip">
        <StatCell label="// duration"  :value="formatDuration(flight.duration_sec)" />
        <StatCell label="// distance"  :value="`${flight.distance_km.toFixed(1)}`" unit="km" />
        <StatCell label="// max alt"   :value="`${flight.max_alt_m}`"               unit="m"
          :alert="flight.max_alt_m > 120" />
        <StatCell label="// max speed" :value="`${flight.max_speed_ms.toFixed(1)}`" unit="m/s" />
        <StatCell label="// batt end"  :value="`${flight.batt_end_pct}`"             unit="%"
          :warn="flight.batt_end_pct < 35" />
        <StatCell label="// drone"     :value="flight.drone_model" />
      </div>

      <!-- Map -->
      <FlightMap
        class="detail-map"
        :path="flight.raw_path || []"
        :mission-id="flight.mission_id"
        :home-lat="flight.home_lat"
        :home-lon="flight.home_lon"
        :progress="replayProgress"
      />

      <!-- Telemetry charts 2×2 -->
      <div class="charts-grid">
        <TelemetryChart :data="altData"   title="// altitude"  unit="m"    color="#f59e0b" :height="140" />
        <TelemetryChart :data="speedData" title="// speed"     unit="m/s"  color="#14b8a6" :height="140" />
        <TelemetryChart :data="battData"  title="// battery"   unit="%"    color="#818cf8" :height="140" />
        <TelemetryChart :data="rcData"    title="// rc signal" unit="%"    color="#22c55e" :height="140" />
      </div>

      <!-- Anomalies -->
      <div class="anomalies-section" v-if="anomalies.length">
        <div class="section-title">// anomalies detected ({{ anomalies.length }})</div>
        <div class="anomaly-list">
          <div
            v-for="(ev, i) in anomalies"
            :key="i"
            class="anomaly-row"
            :class="ev.level"
          >
            <span class="a-time">{{ formatFlightTime(ev.t) }}</span>
            <span class="a-level">{{ ev.level.toUpperCase() }}</span>
            <span class="a-msg">{{ ev.msg }}</span>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div class="notes-section">
        <div class="section-title">// mission notes</div>
        <textarea
          class="notes-input"
          v-model="notes"
          placeholder="Add mission notes..."
          rows="3"
        />
        <button class="btn save-btn" @click="saveNotes">SAVE NOTES</button>
      </div>
    </template>

    <div v-else class="not-found">
      <p>// MISSION NOT FOUND</p>
      <button class="btn" @click="$router.push('/')">← RETURN TO DASHBOARD</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import LoadingSpinner  from '../components/common/LoadingSpinner.vue'
import FlightMap       from '../components/maps/FlightMap.vue'
import TelemetryChart  from '../components/charts/TelemetryChart.vue'
import { formatDuration, formatFlightTime, exportFlightCsv, exportFlightGpx, exportFlightKml } from '../utils/helpers'
import api from '../utils/api'

const route  = useRoute()
const router = useRouter()
const store  = useStore()

const flight   = ref(null)
const loading  = ref(true)
const notes    = ref('')
const anomalies = ref([])
const replaying      = ref(false)
const replayProgress = ref(1)
let replayRaf = null, replayStart = null

onMounted(async () => {
  try {
    const { data } = await api.get(`/flights/${route.params.id}`)
    flight.value = data
    notes.value  = data.notes || ''
    const anRes  = await api.get(`/analytics/anomalies/${route.params.id}`)
    anomalies.value = anRes.data
  } catch {
    flight.value = null
  } finally {
    loading.value = false
  }
})

function toggleReplay() {
  if (replaying.value) { replaying.value = false; cancelAnimationFrame(replayRaf); return }
  replaying.value = true
  replayProgress.value = 0
  replayStart = null
  const dur = (flight.value?.duration_sec ?? 600) * 1000 / 8
  function tick(now) {
    if (!replayStart) replayStart = now
    const p = Math.min(1, (now - replayStart) / dur)
    replayProgress.value = p
    if (p < 1 && replaying.value) replayRaf = requestAnimationFrame(tick)
    else replaying.value = false
  }
  replayRaf = requestAnimationFrame(tick)
}

function doExport(fmt) {
  if (!flight.value) return
  if (fmt === 'csv') exportFlightCsv(flight.value)
  if (fmt === 'gpx') exportFlightGpx(flight.value)
  if (fmt === 'kml') exportFlightKml(flight.value)
}

async function saveNotes() {
  await api.patch(`/flights/${route.params.id}`, { notes: notes.value })
}

async function confirmDelete() {
  if (!confirm(`Delete mission ${flight.value?.mission_id}? This cannot be undone.`)) return
  await store.dispatch('flights/delete', route.params.id)
  router.push('/')
}

const telemetry = computed(() => flight.value?.telemetry ?? [])
const altData   = computed(() => telemetry.value.map(s => s.alt_m    ?? 0))
const speedData = computed(() => telemetry.value.map(s => s.speed_ms ?? 0))
const battData  = computed(() => telemetry.value.map(s => s.batt_pct ?? 0))
const rcData    = computed(() => telemetry.value.map(s => s.rc_signal ?? 0))
</script>

<style scoped>
.flight-detail { display: flex; flex-direction: column; min-height: calc(100vh - 60px); }

.detail-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-panel);
  flex-wrap: wrap;
}

.back-btn {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 1px;
  padding: 5px 10px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
}
.back-btn:hover { border-color: var(--amber); color: var(--amber); }

.header-center { display: flex; align-items: center; gap: 10px; flex: 1; }

.mission-id {
  font-family: var(--font-display);
  font-size: 16px;
  letter-spacing: 2px;
  color: var(--amber-bright);
}

.source-badge {
  font-size: 9px; padding: 2px 7px; border-radius: 2px; border: 1px solid;
  letter-spacing: 1px;
}
.source-badge.dji    { border-color: rgba(245,158,11,0.4); color: var(--amber); }
.source-badge.litchi { border-color: rgba(34,197,94,0.4);  color: #4ade80; }
.source-badge.manual { border-color: rgba(99,102,241,0.4); color: #818cf8; }

.header-actions { display: flex; gap: 6px; flex-wrap: wrap; }

.btn {
  font-family: var(--font-mono); font-size: 10px; letter-spacing: 1px;
  padding: 5px 12px; border: 1px solid var(--border); background: transparent;
  color: var(--text-dim); cursor: pointer; border-radius: 2px; transition: all 0.15s;
  text-transform: uppercase;
}
.btn:hover { border-color: var(--amber); color: var(--amber); background: var(--amber-glow); }
.btn.danger { border-color: rgba(239,68,68,0.4); color: #f87171; }
.btn.danger:hover { background: rgba(239,68,68,0.1); border-color: var(--red); }

.stats-strip {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.detail-map { height: 320px; flex-shrink: 0; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px solid var(--border);
}
.charts-grid > * { border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.charts-grid > *:nth-child(2n) { border-right: none; }

.anomalies-section { border-bottom: 1px solid var(--border); }
.notes-section { padding: 16px 20px; }

.section-title {
  font-size: 10px; letter-spacing: 2px; color: var(--text-dim);
  text-transform: uppercase; padding: 10px 20px 6px;
}

.anomaly-list { padding: 0 20px 10px; display: flex; flex-direction: column; gap: 2px; }

.anomaly-row {
  display: flex; gap: 12px; padding: 5px 10px;
  font-size: 11px; border-radius: 2px; border-left: 2px solid transparent;
}
.anomaly-row.warn     { border-left-color: #fbbf24; background: rgba(251,191,36,0.06); }
.anomaly-row.critical { border-left-color: var(--red); background: rgba(239,68,68,0.07); }

.a-time  { color: var(--text-faint); min-width: 44px; font-size: 10px; }
.a-level { font-size: 9px; letter-spacing: 1px; min-width: 56px;
  color: #fbbf24; }
.anomaly-row.critical .a-level { color: #f87171; }
.a-msg   { color: var(--text-dim); }

.notes-input {
  width: 100%;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  color: var(--text-main);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 10px 12px;
  border-radius: 2px;
  resize: vertical;
  outline: none;
  margin-bottom: 10px;
}
.notes-input:focus { border-color: var(--border-hover); }

.save-btn { padding: 6px 16px; }

.not-found {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 20px; color: var(--text-faint);
}
.not-found p { font-size: 12px; letter-spacing: 3px; }
</style>

<!-- StatCell sub-component inline -->
<script>
import { defineComponent, h } from 'vue'

export const StatCell = defineComponent({
  props: {
    label: String,
    value: [String, Number],
    unit:  { type: String, default: '' },
    alert: { type: Boolean, default: false },
    warn:  { type: Boolean, default: false },
  },
  setup(props) {
    return () => h('div', { style: 'padding:12px 16px; border-right:1px solid var(--border)' }, [
      h('div', { style: 'font-size:9px;letter-spacing:2px;color:var(--text-faint);text-transform:uppercase;margin-bottom:5px' }, props.label),
      h('div', {
        style: `font-family:var(--font-display);font-size:18px;font-weight:700;color:${
          props.alert ? 'var(--red)' : props.warn ? '#fbbf24' : 'var(--amber-bright)'
        };line-height:1`
      }, [
        props.value,
        props.unit && h('span', { style: 'font-family:var(--font-mono);font-size:10px;color:var(--text-dim);margin-left:3px' }, props.unit),
      ]),
    ])
  },
})
</script>
