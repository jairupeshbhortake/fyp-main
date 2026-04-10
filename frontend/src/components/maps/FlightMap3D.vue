<template>
  <div class="flight-map-3d" ref="containerRef">
    <div class="hud-corner tl"></div>
    <div class="hud-corner tr"></div>
    <div class="hud-corner bl"></div>
    <div class="hud-corner br"></div>
    <div class="hud-info">
      <span class="hud-mission">{{ missionId || 'STANDBY' }} (3D VISUALIZER)</span>
      <span class="hud-coords" v-if="homeLat || homeLon">
        HOME: {{ homeLat.toFixed(4) }}°  {{ homeLon.toFixed(4) }}°
      </span>
    </div>
    <div class="hud-controls" v-if="path.length">
      <button class="center-btn" @click="centerOnDrone" title="Locate Drone">⌖</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

const props = defineProps({
  path:      { type: Array,  default: () => [] },
  missionId: { type: String, default: '' },
  homeLat:   { type: Number, default: 0 },
  homeLon:   { type: Number, default: 0 },
  progress:  { type: Number, default: 1 },
})

const containerRef = ref(null)

let scene, camera, renderer, controls, reqId
let pathLine = null
let droneMesh = null
let currentMissionId = null

function init() {
  const W = containerRef.value.clientWidth
  const H = containerRef.value.clientHeight

  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x0d1b2a, 0.0004)

  camera = new THREE.PerspectiveCamera(60, W / H, 1, 20000)
  camera.position.set(0, 400, 800)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(W, H)
  renderer.setPixelRatio(window.devicePixelRatio)
  containerRef.value.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.maxPolarAngle = Math.PI / 2 - 0.02

  const grid = new THREE.GridHelper(10000, 200, 0x00f2fe, 0x4facfe)
  grid.material.opacity = 0.15
  grid.material.transparent = true
  scene.add(grid)

  window.addEventListener('resize', onWindowResize)
  animate()
}

function onWindowResize() {
  if (!containerRef.value || !renderer || !camera) return
  const W = containerRef.value.clientWidth
  const H = containerRef.value.clientHeight
  camera.aspect = W / H
  camera.updateProjectionMatrix()
  renderer.setSize(W, H)
}

function animate() {
  reqId = requestAnimationFrame(animate)
  if (controls) controls.update()
  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

function drawPath() {
  if (!scene) return

  if (pathLine) { scene.remove(pathLine); pathLine.geometry.dispose(); pathLine.material.dispose(); pathLine = null }
  if (droneMesh) { scene.remove(droneMesh); droneMesh.geometry.dispose(); droneMesh.material.dispose(); droneMesh = null }

  if (!props.path || !props.path.length) return

  const homeLatRad = props.homeLat * Math.PI / 180
  const latToM = 111320
  const lonToM = 111320 * Math.cos(homeLatRad)

  const points = []
  props.path.forEach(p => {
    const x = (p.lon - props.homeLon) * lonToM
    const z = -(p.lat - props.homeLat) * latToM
    const y = p.alt || 0
    points.push(new THREE.Vector3(x, y, z))
  })

  const endIdx = Math.max(1, Math.round(props.progress * points.length))
  const visiblePoints = points.slice(0, endIdx)

  const geometry = new THREE.BufferGeometry().setFromPoints(visiblePoints)
  const material = new THREE.LineBasicMaterial({
    color: 0x00f2fe,
    linewidth: 2,
  })

  pathLine = new THREE.Line(geometry, material)
  scene.add(pathLine)

  if (visiblePoints.length > 0) {
    const lastPt = visiblePoints[visiblePoints.length - 1]
    const dGeo = new THREE.SphereGeometry(10, 16, 16)
    const dMat = new THREE.MeshBasicMaterial({ color: 0xffffff })
    droneMesh = new THREE.Mesh(dGeo, dMat)
    droneMesh.position.copy(lastPt)
    scene.add(droneMesh)

    // Fit camera on new mission
    if (currentMissionId !== props.missionId) {
      currentMissionId = props.missionId
      const fullGeom = new THREE.BufferGeometry().setFromPoints(points)
      fullGeom.computeBoundingBox()
      const center = new THREE.Vector3()
      if (fullGeom.boundingBox) {
        fullGeom.boundingBox.getCenter(center)
        controls.target.copy(center)
        camera.position.set(center.x + 300, Math.max(center.y + 400, 400), center.z + 600)
      }
      fullGeom.dispose()
    }
  }
}

function centerOnDrone() {
  if (!controls || !camera || !props.path.length) return

  const homeLatRad = props.homeLat * Math.PI / 180
  const latToM = 111320
  const lonToM = 111320 * Math.cos(homeLatRad)

  const points = []
  props.path.forEach(p => {
    const x = (p.lon - props.homeLon) * lonToM
    const z = -(p.lat - props.homeLat) * latToM
    const y = p.alt || 0
    points.push(new THREE.Vector3(x, y, z))
  })

  const fullGeom = new THREE.BufferGeometry().setFromPoints(points)
  fullGeom.computeBoundingBox()
  const center = new THREE.Vector3()
  
  if (fullGeom.boundingBox) {
    fullGeom.boundingBox.getCenter(center)
    controls.target.copy(center)
    
    const size = new THREE.Vector3()
    fullGeom.boundingBox.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z) || 100
    
    const fovRad = camera.fov * (Math.PI / 180)
    const dist = Math.abs((maxDim / 2) / Math.tan(fovRad / 2)) * 1.5
    
    camera.position.set(center.x + dist * 0.3, Math.max(center.y + dist * 0.5, 200), center.z + dist)
    controls.update()
  }
  fullGeom.dispose()
}

onMounted(() => {
  init()
  drawPath()
  setTimeout(onWindowResize, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', onWindowResize)
  cancelAnimationFrame(reqId)
  if (renderer) renderer.dispose()
})

watch(() => [props.path, props.progress], drawPath, { deep: true })
</script>

<style scoped>
.flight-map-3d {
  position: relative;
  width: 100%;
  flex: 1;
  min-height: 300px;
  overflow: hidden;
  border-bottom: 1px solid var(--glass-border);
  background: radial-gradient(circle at center, #0d1b2a 0%, #030a11 100%);
  cursor: grab;
}
.flight-map-3d:active { cursor: grabbing; }

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
