<template>
  <div class="chart-wrap">
    <div class="chart-header">
      <span class="chart-title" :style="{ color: color }">{{ title }}</span>
      <span class="chart-peak">peak: {{ peakVal }}{{ unit }}</span>
    </div>
    <div class="chart-canvas-wrap">
      <canvas ref="canvasRef" class="chart-canvas" :height="height"/>
      <div v-show="progress < 1" class="chart-indicator" :style="{ left: progress * 100 + '%' }">
        <div class="indicator-line" :style="{ background: color }"></div>
        <div class="indicator-dot" :style="{ borderColor: color }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  data:   { type: Array, default: () => [] },
  title:  { type: String, default: '' },
  unit:   { type: String, default: '' },
  color:  { type: String, default: '#f59e0b' },
  height: { type: Number, default: 120 },
  progress: { type: Number, default: 1 },
})

const canvasRef = ref(null)
let ro = null



import { computed } from 'vue'
const peakVal = computed(() => props.data.length ? Math.max(...props.data).toFixed(1) : 0)

function draw() {
  const canvas = canvasRef.value
  if (!canvas || !props.data.length) return
  const ctx = canvas.getContext('2d')
  const W = canvas.offsetWidth
  const H = props.height
  canvas.width = W
  canvas.height = H

  ctx.clearRect(0, 0, W, H)

  const data = props.data
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  // Grid lines & Y-axis labels
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
  ctx.lineWidth = 1
  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'left'

  const getY = (val) => H - ((val - min) / range) * (H - 12) - 4
  const ticks = 4

  for (let i = 0; i <= ticks; i++) {
    const val = min + (range / ticks) * i
    const y = getY(val)
    
    // Draw grid line for inner ticks
    if (i > 0 && i < ticks) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
    }
    
    // Draw tick label
    ctx.textBaseline = i === 0 ? 'bottom' : i === ticks ? 'top' : 'middle'
    const labelY = i === 0 ? y - 2 : i === ticks ? y + 2 : y - 3
    ctx.fillText(Math.round(val), 4, labelY)
  }

  const xStep = W / (data.length - 1)

  // Fill
  const grad = ctx.createLinearGradient(0, 0, 0, H)
  grad.addColorStop(0, props.color + '55')
  grad.addColorStop(1, props.color + '05')

  ctx.beginPath()
  data.forEach((v, i) => {
    const x = i * xStep
    const y = H - ((v - min) / range) * (H - 12) - 4
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  })
  ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath()
  ctx.fillStyle = grad
  ctx.fill()

  // Line
  ctx.beginPath()
  ctx.strokeStyle = props.color
  ctx.lineWidth = 1.5
  ctx.lineJoin = 'round'
  data.forEach((v, i) => {
    const x = i * xStep
    const y = H - ((v - min) / range) * (H - 12) - 4
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  })
  ctx.stroke()
}

onMounted(() => {
  draw()
  ro = new ResizeObserver(draw)
  if (canvasRef.value?.parentElement) ro.observe(canvasRef.value.parentElement)
})

onUnmounted(() => ro?.disconnect())

watch(() => props.data, draw, { deep: true })
</script>

<style scoped>
.chart-wrap {
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 4px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.chart-peak { 
  font-family: var(--font-body);
  font-size: 11px; 
  color: var(--text-dim); 
}

.chart-canvas-wrap {
  position: relative;
  width: 100%;
}

.chart-canvas { width: 100%; display: block; }

.chart-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  pointer-events: none;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.indicator-line {
  width: 1px;
  height: 100%;
  opacity: 0.8;
}

.indicator-dot {
  position: absolute;
  top: -3px; 
  width: 6px;
  height: 6px;
  border-radius: 50%;
  border: 1.5px solid;
  background: var(--bg-card, #1e293b);
}
</style>
