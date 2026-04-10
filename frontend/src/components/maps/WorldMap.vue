<template>
  <div ref="mapEl" class="world-map-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  locations: { type: Array, default: () => [] },  // [{lat, lon, mission_id, id}]
})

const mapEl = ref(null)
let map = null
const markers = []

const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'

function markerIcon(missionId) {
  return L.divIcon({
    className: '',
    html: `<div class="world-marker" title="${missionId}"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  })
}

function plotLocations() {
  if (!map) return
  markers.forEach(m => map.removeLayer(m))
  markers.length = 0

  props.locations.forEach(loc => {
    if (!loc.lat || !loc.lon) return
    const m = L.marker([loc.lat, loc.lon], { icon: markerIcon(loc.mission_id) })
      .bindTooltip(loc.mission_id, { className: 'skytraq-tooltip', direction: 'top' })
      .addTo(map)
    markers.push(m)
  })

  if (props.locations.length) {
    const latLngs = props.locations.filter(l => l.lat && l.lon).map(l => [l.lat, l.lon])
    if (latLngs.length > 1) {
      map.fitBounds(latLngs, { padding: [40, 40], maxZoom: 10 })
    } else if (latLngs.length === 1) {
      map.setView(latLngs[0], 10)
    }
  }
}

onMounted(() => {
  map = L.map(mapEl.value, {
    zoomControl: true,
    attributionControl: false,
  })
  L.tileLayer(TILE_URL, { maxZoom: 18 }).addTo(map)
  map.setView([20, 0], 2)
  plotLocations()
  
  // Ensure map renders correctly after DOM settles or resizes
  const resizeObserver = new ResizeObserver(() => {
    if (map) map.invalidateSize()
  })
  resizeObserver.observe(mapEl.value)
  
  // Backup timeout
  setTimeout(() => {
    if (map) map.invalidateSize()
  }, 500)

  // Attach to element for cleanup access
  mapEl.value._resizeObserver = resizeObserver
})

watch(() => props.locations, plotLocations, { deep: true })

onUnmounted(() => { 
  if (map) { map.remove(); map = null }
  if (mapEl.value?._resizeObserver) {
    mapEl.value._resizeObserver.disconnect()
  }
})
</script>

<style>
.world-marker {
  width: 12px; height: 12px;
  background: #00f2fe;
  border-radius: 50%;
  border: 2px solid rgba(0,242,254,0.5);
  box-shadow: 0 0 10px #00f2fe, 0 0 24px rgba(0,242,254,0.3);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 8px #00f2fe; }
  50%  { box-shadow: 0 0 20px #00f2fe, 0 0 40px rgba(0,242,254,0.4); }
}
</style>

<style scoped>
.world-map-container {
  width: 100%;
  height: 100%;
  min-height: 340px;
  background: #0d1b2a;
  border-radius: var(--radius-md);
  overflow: hidden;
  z-index: 1;
}
</style>
