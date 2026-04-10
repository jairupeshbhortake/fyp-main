<template>
  <div class="dashboard">
    <StatsCards />

    <div class="dashboard-body">
      <!-- Left sidebar -->
      <aside class="sidebar">
        <FiltersPanel />
        <FlightList :selected-id="selectedId" @select="onSelectFlight" />
      </aside>

      <!-- Main area -->
      <main class="main-area">
        <div class="flight-header" v-if="selectedFlight">
          <span class="mission-id">{{ selectedFlight.mission_id }}</span>
          <div class="header-tags">
            <span
              v-for="tag in selectedFlight.tags"
              :key="tag.label"
              class="tag"
              :class="`tag-${tag.kind}`"
            >{{ tag.label }}</span>
          </div>
          <div class="header-actions">
            <button class="btn" @click="toggleReplay">
              {{ replaying ? '⏹ STOP' : '▶ REPLAY' }}
            </button>
            <button class="btn" @click="show3D = !show3D" :class="{ primary: show3D }">
              {{ show3D ? '2D MAP' : '3D VIEW' }}
            </button>
            <label class="btn primary" style="cursor: pointer; margin: 0; margin-left: 8px;">
               + UPLOAD MORE
              <input type="file" accept=".txt,.csv" @change="handleUpload" hidden />
            </label>
          </div>
        </div>
        <div class="flight-header" v-else>
          <span class="mission-id" style="opacity: 0.5;">AWAITING FLIGHT LOG...</span>
          <div class="header-actions">
            <label class="btn primary" style="cursor: pointer; margin: 0;">
               + UPLOAD FLIGHT LOG
              <input type="file" accept=".txt,.csv" @change="handleUpload" hidden />
            </label>
          </div>
        </div>

        <FlightMap
          v-if="!show3D"
          :path="selectedFlight?.raw_path || []"
          :mission-id="selectedFlight?.mission_id || 'STANDBY'"
          :home-lat="selectedFlight?.home_lat || 0"
          :home-lon="selectedFlight?.home_lon || 0"
          :progress="replayProgress"
        />
        <FlightMap3D
          v-else
          :path="selectedFlight?.raw_path || []"
          :mission-id="selectedFlight?.mission_id || 'STANDBY'"
          :home-lat="selectedFlight?.home_lat || 0"
          :home-lon="selectedFlight?.home_lon || 0"
          :progress="replayProgress"
        />

        <div class="telemetry-grid">
          <TelemetryChart :data="altData"   :progress="replayProgress" title="Altitude"  unit="m"   color="#4facfe" />
          <TelemetryChart :data="speedData" :progress="replayProgress" title="Speed"     unit="m/s" color="#00f2fe" />
          <TelemetryChart :data="battData"  :progress="replayProgress" title="Battery"   unit="%"   color="#818cf8" />
          <TelemetryChart :data="rcData"    :progress="replayProgress" title="RC Signal" unit="%"   color="#22c55e" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import StatsCards   from '../components/dashboard/StatsCards.vue'
import FiltersPanel from '../components/dashboard/FiltersPanel.vue'
import FlightList   from '../components/dashboard/FlightList.vue'
import FlightMap    from '../components/maps/FlightMap.vue'
import FlightMap3D  from '../components/maps/FlightMap3D.vue'
import TelemetryChart from '../components/charts/TelemetryChart.vue'

const store = useStore()
const show3D = ref(false)

const selectedFlight = computed(() => store.state.flights.selectedFlight)
const selectedId     = computed(() => selectedFlight.value?.id)
const replaying      = ref(false)
const replayProgress = ref(1)

let replayRaf = null
let replayStart = null

watch(() => selectedId.value, () => {
  replaying.value = false
  replayProgress.value = 1
})

onMounted(async () => {
  await store.dispatch('flights/fetchAll')
  await store.dispatch('analytics/fetchOverview')
})

function onSelectFlight(f) {
  store.dispatch('flights/selectFlight', f.id)
}

function toggleReplay() {
  if (replaying.value) {
    replaying.value = false
    cancelAnimationFrame(replayRaf)
    return
  }
  replaying.value = true
  replayProgress.value = 0
  replayStart = null

  const dur = (selectedFlight.value?.duration_sec ?? 600) * 1000 / 8

  function tick(now) {
    if (!replayStart) replayStart = now
    const p = Math.min(1, (now - replayStart) / dur)
    replayProgress.value = p
    if (p < 1 && replaying.value) replayRaf = requestAnimationFrame(tick)
    else replaying.value = false
  }
  replayRaf = requestAnimationFrame(tick)
}

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    await store.dispatch('flights/upload', file)
    await store.dispatch('analytics/fetchOverview')
  } catch {}
  e.target.value = ''
}

// Telemetry series derived from selected flight
const telemetry = computed(() => selectedFlight.value?.telemetry ?? [])
const altData   = computed(() => telemetry.value.map(s => s.alt_m   ?? 0))
const speedData = computed(() => telemetry.value.map(s => s.speed_ms ?? 0))
const battData  = computed(() => telemetry.value.map(s => s.batt_pct ?? 0))
const rcData    = computed(() => telemetry.value.map(s => s.rc_signal ?? 0))
</script>

<style scoped>
.dashboard { 
  display: flex; flex-direction: column; 
  height: calc(100vh - var(--topbar-h)); 
  overflow: hidden; 
  padding: 16px 24px 24px; 
  gap: 16px;
}

.dashboard-body { display: flex; flex: 1; overflow: hidden; gap: 16px; }

.sidebar {
  width: var(--sidebar-w);
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: var(--glass-shadow);
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  overflow-y: auto;
  box-shadow: var(--glass-shadow);
  min-width: 0;
}

.flight-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.02);
  flex-wrap: wrap;
  flex-shrink: 0;
}

.mission-id {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-main);
}

.header-tags { display: flex; gap: 6px; flex: 1; }

.header-actions { display: flex; gap: 8px; margin-left: auto; }

.telemetry-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid var(--glass-border);
  background: rgba(0,0,0,0.2);
  flex-shrink: 0;
}

.telemetry-grid > * { border-right: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); }
.telemetry-grid > *:nth-child(2n) { border-right: none; }
</style>
