<template>
  <div class="heatmap-wrap">
    <div class="heatmap-header">
      <span class="section-label">// activity heatmap</span>
      <span class="sub">Flight start locations</span>
    </div>
    <svg class="heatmap-svg" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet">
      <defs>
        <radialGradient v-for="p in points" :key="p.id" :id="`hg-${p.id}`" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   :stop-color="p.color" stop-opacity="0.7"/>
          <stop offset="100%" :stop-color="p.color" stop-opacity="0"/>
        </radialGradient>
        <pattern id="hmgrid" width="30" height="30" patternUnits="userSpaceOnUse">
          <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(245,158,11,0.05)" stroke-width="1"/>
        </pattern>
      </defs>
      <rect :width="W" :height="H" fill="#070c09"/>
      <rect :width="W" :height="H" fill="url(#hmgrid)"/>
      <ellipse v-for="p in points" :key="p.id"
        :cx="p.x" :cy="p.y" :rx="p.r" :ry="p.r"
        :fill="`url(#hg-${p.id})`"
      />
      <circle v-for="p in points" :key="`dot-${p.id}`"
        :cx="p.x" :cy="p.y" r="3" :fill="p.color" opacity="0.9"
      />
    </svg>
    <p class="heatmap-note">
      Connect a mapping library (Leaflet / MapLibre) for real geographic rendering.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const W = 600, H = 260
const store = useStore()
const flights = computed(() => store.state.flights.list)

// Project flight home coordinates to SVG viewport (simplified equirectangular)
const points = computed(() => {
  const fs = flights.value.filter(f => f.home_lat && f.home_lon)
  if (!fs.length) return []
  const lats = fs.map(f => f.home_lat)
  const lons = fs.map(f => f.home_lon)
  const minLat = Math.min(...lats), maxLat = Math.max(...lats)
  const minLon = Math.min(...lons), maxLon = Math.max(...lons)
  const pad = 40
  return fs.map((f, i) => ({
    id: f.id ?? i,
    x: pad + ((f.home_lon - minLon) / (maxLon - minLon + 0.001)) * (W - pad * 2),
    y: H - pad - ((f.home_lat - minLat) / (maxLat - minLat + 0.001)) * (H - pad * 2),
    r: 30 + (f.duration_sec / 3600) * 20,
    color: f.batt_end_pct < 25 ? '#ef4444' : f.max_alt_m > 120 ? '#fbbf24' : '#f59e0b',
  }))
})
</script>

<style scoped>
.heatmap-wrap {
  border: 1px solid var(--border);
  border-radius: 2px;
  overflow: hidden;
  background: var(--bg-card);
}

.heatmap-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
}

.section-label { font-size: 10px; letter-spacing: 2px; color: var(--text-dim); text-transform: uppercase; }
.sub { font-size: 10px; color: var(--text-faint); }

.heatmap-svg { width: 100%; display: block; }

.heatmap-note {
  font-size: 9px;
  color: var(--text-faint);
  letter-spacing: 0.5px;
  padding: 6px 14px;
  border-top: 1px solid var(--border);
}
</style>
