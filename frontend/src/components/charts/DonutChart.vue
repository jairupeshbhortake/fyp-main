<template>
  <div class="donut-wrap">
    <div class="donut-title">{{ title }}</div>
    <div class="donut-body">
      <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="donut-svg">
        <circle :cx="C" :cy="C" :r="R" fill="none" stroke="rgba(255,255,255,0.05)" :stroke-width="THICK"/>
        <circle
          v-for="(seg, i) in segments" :key="i"
          :cx="C" :cy="C" :r="R"
          fill="none"
          :stroke="seg.color"
          :stroke-width="THICK"
          :stroke-dasharray="`${seg.dash} ${CIRC - seg.dash}`"
          :stroke-dashoffset="seg.offset"
          stroke-linecap="round"
          style="transition: stroke-dasharray 0.6s ease"
        />
        <text :x="C" :y="C - 6" text-anchor="middle" class="center-num" dominant-baseline="middle">{{ total }}</text>
        <text :x="C" :y="C + 14" text-anchor="middle" class="center-label">FLIGHTS</text>
      </svg>
      <div class="legend">
        <div v-for="(seg, i) in segments" :key="i" class="legend-row">
          <span class="legend-dot" :style="{ background: seg.color }"></span>
          <span class="legend-name">{{ seg.label }}</span>
          <span class="legend-val">{{ seg.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title:  { type: String, default: 'Chart' },
  data:   { type: Object, default: () => ({}) },
  colors: {
    type: Array,
    default: () => ['#00f2fe','#4facfe','#818cf8','#34d399','#f59e0b','#f87171','#a78bfa','#38bdf8'],
  },
})

const SIZE  = 180
const C     = SIZE / 2
const R     = 66
const THICK = 22
const CIRC  = 2 * Math.PI * R

const total    = computed(() => Object.values(props.data).reduce((a, b) => a + b, 0) || 0)

const segments = computed(() => {
  const entries = Object.entries(props.data).filter(([, v]) => v > 0)
  const t = total.value || 1
  let offset = CIRC * 0.25
  const GAP = 4
  return entries.map(([label, count], i) => {
    const dash = Math.max((count / t) * CIRC - GAP, 2)
    const seg = { label, count, color: props.colors[i % props.colors.length], dash, offset: -offset + CIRC }
    offset += (count / t) * CIRC
    return seg
  })
})
</script>

<style scoped>
.donut-wrap { display: flex; flex-direction: column; gap: 12px; padding: 20px; }
.donut-title { font-family: var(--font-display); font-size: 13px; font-weight: 600; letter-spacing: 0.5px; color: var(--text-dim); }
.donut-body  { display: flex; align-items: center; gap: 20px; }
.donut-svg   { width: 140px; height: 140px; flex-shrink: 0; overflow: visible; }

.center-num   { font-family: var(--font-display); font-size: 28px; font-weight: 700; fill: #f8fafc; }
.center-label { font-family: var(--font-body); font-size: 9px; fill: var(--text-faint); letter-spacing: 1.5px; }

.legend      { display: flex; flex-direction: column; gap: 8px; min-width: 0; flex: 1; }
.legend-row  { display: flex; align-items: center; gap: 8px; }
.legend-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-name { font-size: 11px; color: var(--text-dim); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.legend-val  { font-family: var(--font-display); font-size: 13px; font-weight: 600; color: var(--text-main); min-width: 24px; text-align: right; }
</style>
