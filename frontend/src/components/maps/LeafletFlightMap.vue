<template>
  <div ref="mapEl" class="leaflet-map-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  path:      { type: Array,  default: () => [] },   // [{lat, lon, alt, t}]
  missionId: { type: String, default: '' },
  homeLat:   { type: Number, default: 0 },
  homeLon:   { type: Number, default: 0 },
  progress:  { type: Number, default: 1 },          // 0..1 for replay
})

const mapEl = ref(null)
let map = null
let polyline = null
let homeMarker = null
let droneMarker = null

// Map Layer Definitions
const baseMaps = {
  "Dark": L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }),
  "Physical": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }),
  "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }),
  "Terrain": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', { maxZoom: 17 })
}

function buildPolyline() {
  const pts = props.path.map(p => [p.lat, p.lon])
  return pts
}

function droneIcon() {
  return L.divIcon({
    className: '',
    html: `<div class="drone-dot"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  })
}

function homeIcon() {
  return L.divIcon({
    className: '',
    html: `<div class="home-dot"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  })
}

function drawPath() {
  if (!map) return

  // Remove old layers
  if (polyline) { map.removeLayer(polyline); polyline = null }
  if (homeMarker) { map.removeLayer(homeMarker); homeMarker = null }
  if (droneMarker) { map.removeLayer(droneMarker); droneMarker = null }

  const pts = buildPolyline()
  if (!pts.length) return

  // Replay slicing
  const endIdx = Math.max(1, Math.round(props.progress * pts.length))
  const visible = pts.slice(0, endIdx)

  polyline = L.polyline(visible, {
    color: '#4facfe',
    weight: 3,
    opacity: 0.9,
  }).addTo(map)

  // Home marker
  if (props.homeLat && props.homeLon) {
    homeMarker = L.marker([props.homeLat, props.homeLon], { icon: homeIcon() })
      .bindTooltip(props.missionId, { className: 'dronevault-tooltip', direction: 'top' })
      .addTo(map)
  }

  // Drone at current position
  const last = visible[visible.length - 1]
  droneMarker = L.marker(last, { icon: droneIcon() }).addTo(map)

  // Fit bounds
  if (props.progress >= 1) {
    map.fitBounds(polyline.getBounds(), { padding: [30, 30] })
  }
}

onMounted(() => {
  map = L.map(mapEl.value, {
    zoomControl: true,
    attributionControl: false,
    layers: [baseMaps["Dark"]] // Default map
  })

  // Add map style toggler below the zoom controls
  L.control.layers(baseMaps, null, { position: 'topleft' }).addTo(map)

  // Fallback center if no path yet
  map.setView([20, 0], 2)

  drawPath()
})

watch(() => [props.path, props.progress], drawPath, { deep: true })

function centerOnDrone() {
  if (!map || !props.path.length) return
  const pts = props.path.map(p => [p.lat, p.lon])
  const bounds = L.latLngBounds(pts)
  map.fitBounds(bounds, { padding: [30, 30], animate: true })
}

defineExpose({ centerOnDrone })
</script>

<style>
/* Global — leaflet tooltip custom style */
.dronevault-tooltip {
  background: rgba(15,23,42,0.95);
  border: 1px solid rgba(0,242,254,0.4);
  color: #00f2fe;
  font-size: 11px;
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 6px;
  padding: 4px 10px;
  box-shadow: 0 4px 20px rgba(0,242,254,0.2);
}
.drone-dot {
  width: 14px; height: 14px;
  background: #00f2fe;
  border-radius: 50%;
  border: 2px solid rgba(0,242,254,0.4);
  box-shadow: 0 0 12px #00f2fe;
}
.home-dot {
  width: 10px; height: 10px;
  background: #4facfe;
  border-radius: 50%;
  border: 2px solid rgba(79,172,254,0.5);
  box-shadow: 0 0 8px #4facfe;
}

/* Glassmorphism Map Layer Controls */
.leaflet-control-layers {
  background: rgba(15,23,42,0.85) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(0, 242, 254, 0.4) !important;
  border-radius: 8px !important;
  color: #a0aec0 !important;
  font-family: 'Outfit', sans-serif !important;
  padding: 6px !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
  transition: all 0.3s ease;
}
.leaflet-control-layers:hover {
  border-color: rgba(0, 242, 254, 0.8) !important;
}
.leaflet-control-layers-list {
  padding: 4px;
}
.leaflet-control-layers label {
  color: #e2e8f0;
  font-size: 13px;
  margin-bottom: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.leaflet-control-layers-selector {
  margin-right: 8px !important;
  accent-color: #00f2fe;
}
.leaflet-control-layers-expanded {
  padding: 10px 14px !important;
}
.leaflet-control-layers-toggle {
  background-color: transparent !important;
  border-radius: 8px !important;
}
</style>

<style scoped>
.leaflet-map-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
  background: #0d1b2a;
  z-index: 1;
}
</style>
