<template>
  <div class="flight-map-outer">
    <div class="hud-corner tl"></div>
    <div class="hud-corner tr"></div>
    <div class="hud-corner bl"></div>
    <div class="hud-corner br"></div>
    <LeafletFlightMap
      ref="mapRef"
      :path="path"
      :mission-id="missionId"
      :home-lat="homeLat"
      :home-lon="homeLon"
      :progress="progress"
      class="inner-map"
    />
    <!-- HUD overlay -->
    <div class="hud-info">
      <span class="hud-mission">{{ missionId || 'STANDBY' }}</span>
      <span class="hud-coords" v-if="homeLat || homeLon">
        {{ homeLat.toFixed(4) }}°  {{ homeLon.toFixed(4) }}°
      </span>
    </div>
    <div class="hud-controls" v-if="path.length">
      <button class="center-btn" @click="mapRef?.centerOnDrone()" title="Locate Drone">⌖</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LeafletFlightMap from './LeafletFlightMap.vue'

const mapRef = ref(null)

defineProps({
  path:      { type: Array,  default: () => [] },
  missionId: { type: String, default: '' },
  homeLat:   { type: Number, default: 0 },
  homeLon:   { type: Number, default: 0 },
  progress:  { type: Number, default: 1 },
})
</script>

<style scoped>
.flight-map-outer {
  position: relative;
  width: 100%;
  flex: 1;
  min-height: 300px;
  overflow: hidden;
  border-bottom: 1px solid var(--glass-border);
}

.inner-map { position: absolute; inset: 0; }

.hud-corner {
  position: absolute;
  width: 18px; height: 18px;
  border-color: rgba(0, 242, 254, 0.4);
  border-style: solid;
  pointer-events: none;
  z-index: 20;
}
.tl { top: 10px;    left: 10px;    border-width: 2px 0 0 2px; border-radius: 4px 0 0 0; }
.tr { top: 10px;    right: 10px;   border-width: 2px 2px 0 0; border-radius: 0 4px 0 0; }
.bl { bottom: 10px; left: 10px;    border-width: 0 0 2px 2px; border-radius: 0 0 0 4px; }
.br { bottom: 10px; right: 10px;   border-width: 0 2px 2px 0; border-radius: 0 0 4px 0; }

.hud-info {
  position: absolute;
  bottom: 14px;
  left: 20px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 2px;
  pointer-events: none;
}

.hud-mission {
  font-family: 'Outfit', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.8);
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(0,242,254,0.5);
}

.hud-coords {
  font-family: 'Inter', sans-serif;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

.hud-controls {
  position: absolute;
  top: 14px;
  right: 20px;
  z-index: 20;
}

.center-btn {
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(0, 242, 254, 0.4);
  color: #00f2fe;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.center-btn:hover {
  background: rgba(0, 242, 254, 0.2);
  box-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
}
</style>
