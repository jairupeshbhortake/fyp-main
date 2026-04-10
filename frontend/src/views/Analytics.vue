<template>
  <div class="analytics-page">
    <div class="page-header">
      <div class="header-titles">
        <span class="page-title">Flight Analytics</span>
        <span class="page-sub">Aggregate stats across all missions</span>
      </div>
      <button class="btn btn-report" @click="generateReport">
        <span class="icon">📄</span> Generate Report
      </button>
    </div>

    <LoadingSpinner v-if="loading" label="Computing analytics..." />

    <template v-else>
      <!-- KPI strip -->
      <div class="kpi-strip">
        <div class="kpi" v-for="k in kpis" :key="k.label">
          <div class="kpi-label">{{ k.label }}</div>
          <div class="kpi-value">
            {{ k.value }}<span class="kpi-unit">{{ k.unit }}</span>
          </div>
        </div>
      </div>

      <!-- 4 Charts row -->
      <div class="charts-row">
        <div class="chart-card glass-panel">
          <DonutChart title="Flights by Drone"    :data="overview?.flights_by_drone    || {}" />
        </div>
        <div class="chart-card glass-panel">
          <DonutChart title="Flights by Source"   :data="overview?.flights_by_source   || {}"
            :colors="['#f59e0b','#34d399','#818cf8']" />
        </div>
        <div class="chart-card glass-panel">
          <DonutChart title="Flights by Duration" :data="overview?.flights_by_duration_bucket || {}"
            :colors="['#4facfe','#00f2fe','#a78bfa']" />
        </div>
        <div class="chart-card glass-panel">
          <PolarTimeChart title="Flights by Time of Day" :data="overview?.flights_by_hour || {}" />
        </div>
      </div>

      <!-- World Map -->
      <div class="map-section glass-panel">
        <div class="section-header">
          <span class="section-title">Flight Locations</span>
          <span class="section-sub">{{ (overview?.home_locations || []).length }} sites recorded</span>
        </div>
        <div class="world-map-wrap">
          <WorldMap :locations="overview?.home_locations || []" />
        </div>
      </div>

      <!-- Battery vs Flight chart (full width) -->
      <div class="battery-full glass-panel">
        <BatteryTimeChart />
      </div>

      <!-- Bottom row: Leaderboards -->
      <div class="leaderboards-row">
        <div class="lb-card glass-panel">
          <LeaderboardPanel
            title="Top 3 Longest Flights"
            :items="overview?.top_longest || []"
            metric="duration"
          />
        </div>
        <div class="lb-card glass-panel">
          <LeaderboardPanel
            title="Top 3 Furthest Flights"
            :items="overview?.top_furthest || []"
            metric="distance"
            unit="km"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '../utils/api'
import { downloadBlob } from '../utils/helpers'
import LoadingSpinner    from '../components/common/LoadingSpinner.vue'
import DonutChart        from '../components/charts/DonutChart.vue'
import PolarTimeChart    from '../components/charts/PolarTimeChart.vue'
import BatteryTimeChart  from '../components/charts/BatteryTimeChart.vue'
import WorldMap          from '../components/maps/WorldMap.vue'
import LeaderboardPanel  from '../components/dashboard/LeaderboardPanel.vue'

const generateReport = async () => {
  try {
    const { data } = await api.get('/analytics/report/pdf', { responseType: 'blob' })
    downloadBlob(data, 'analytics_report.pdf')
  } catch (error) {
    console.error('Failed to download report', error)
    alert('Failed to generate report')
  }
}

const store    = useStore()
const loading  = computed(() => store.state.analytics.loadingOverview)
const overview = computed(() => store.state.analytics.overview)

onMounted(async () => {
  await store.dispatch('flights/fetchFlights')
  await store.dispatch('analytics/fetchOverview')
  await store.dispatch('analytics/fetchBatteryHealth')
})

const kpis = computed(() => {
  if (!overview.value) return []
  const o = overview.value
  return [
    { label: 'Total Missions',  value: o.total_flights,                   unit: '' },
    { label: 'Total Airtime',   value: o.total_duration_hr?.toFixed(1),   unit: ' hr' },
    { label: 'Total Range',     value: o.total_distance_km?.toFixed(1),   unit: ' km' },
    { label: 'Altitude Record', value: o.max_alt_ever_m,                  unit: ' m' },
    { label: 'Avg Flight',      value: o.avg_duration_min,                unit: ' min' },
    { label: 'Avg Distance',    value: o.avg_distance_km?.toFixed(2),     unit: ' km' },
    { label: 'Top Speed',       value: o.max_speed_ever_ms?.toFixed(1),   unit: ' m/s' },
  ]
})
</script>

<style scoped>
.analytics-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 32px 48px;
  overflow-y: auto;
  height: calc(100vh - var(--topbar-h));
  scroll-behavior: smooth;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-titles {
  display: flex;
  align-items: baseline;
  gap: 14px;
}

.btn-report {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  color: #020617;
  border: none;
}
.btn-report:hover {
  filter: brightness(1.2) saturate(1.1);
  box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
  transform: translateY(-1px);
}
.btn-report:active { transform: translateY(0); }

.page-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-sub { font-size: 13px; color: var(--text-faint); }

/* KPI strip */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  flex-shrink: 0;
}

.kpi {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 16px 18px;
  transition: border-color 0.2s;
}
.kpi:hover { border-color: rgba(0,242,254,0.25); }

.kpi-label {
  font-size: 10px;
  letter-spacing: 0.5px;
  color: var(--text-faint);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.kpi-value {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1;
}

.kpi-unit {
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-faint);
  margin-left: 2px;
}

/* 4 donut charts row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  flex-shrink: 0;
}

.chart-card {
  min-height: 200px;
  overflow: hidden;
}

/* World map section */
.map-section {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--glass-border);
}

.section-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.section-sub { font-size: 12px; color: var(--text-faint); }

.world-map-wrap { 
  height: 400px; 
  flex-shrink: 0;
  background: rgba(0,0,0,0.2);
}

/* Battery full-width */
.battery-full { 
  overflow: hidden; 
  min-height: 450px; 
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

/* Leaderboards row */
.leaderboards-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  flex-shrink: 0;
}

.lb-card { overflow: hidden; }
</style>
