<template>
  <div class="polar-wrap">
    <div class="polar-title">{{ title }}</div>
    <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="polar-svg">
      <defs>
        <radialGradient id="polarGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="rgba(0,242,254,0.08)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
      </defs>

      <!-- Background rings -->
      <circle
        v-for="ring in [0.25, 0.5, 0.75, 1]" :key="ring"
        :cx="C" :cy="C"
        :r="maxR * ring"
        fill="none"
        stroke="rgba(255,255,255,0.04)"
        stroke-width="1"
      />

      <!-- Hour spokes -->
      <line
        v-for="h in 24" :key="`s${h}`"
        :x1="C" :y1="C"
        :x2="C + maxR * Math.cos((h / 24) * TAU - Math.PI / 2)"
        :y2="C + maxR * Math.sin((h / 24) * TAU - Math.PI / 2)"
        stroke="rgba(255,255,255,0.03)"
        stroke-width="1"
      />

      <!-- Bars -->
      <path
        v-for="(bar, i) in bars" :key="i"
        :d="bar.d"
        :fill="bar.color"
        opacity="0.85"
      />

      <!-- Hour labels: 0, 6, 12, 18 -->
      <text
        v-for="lbl in hourLabels" :key="lbl.h"
        :x="lbl.x" :y="lbl.y"
        text-anchor="middle"
        dominant-baseline="middle"
        class="hour-lbl"
      >{{ lbl.text }}</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Flights by Time of Day' },
  data:  { type: Object, default: () => ({}) },  // { "0": count, "1": count, ... "23": count }
})

const SIZE = 200
const C    = SIZE / 2
const maxR = 78
const TAU  = Math.PI * 2

const counts = computed(() => {
  return Array.from({ length: 24 }, (_, h) => Number(props.data[String(h)] ?? 0))
})

const maxCount = computed(() => Math.max(...counts.value, 1))

function polarX(angle, r) { return C + r * Math.cos(angle - Math.PI / 2) }
function polarY(angle, r) { return C + r * Math.sin(angle - Math.PI / 2) }

const bars = computed(() => {
  const N = 24
  const slice = TAU / N
  const gap = 0.06

  const COLORS = ['#00f2fe','#4facfe','#818cf8','#34d399','#f59e0b','#f87171']

  return counts.value.map((count, h) => {
    const r = (count / maxCount.value) * maxR
    if (r < 2) return { d: '', color: 'transparent' }
    const a0 = (h / N) * TAU + gap
    const a1 = ((h + 1) / N) * TAU - gap
    const x0 = polarX(a0, 6), y0 = polarY(a0, 6)
    const x1 = polarX(a1, 6), y1 = polarY(a1, 6)
    const x2 = polarX(a1, r), y2 = polarY(a1, r)
    const x3 = polarX(a0, r), y3 = polarY(a0, r)
    const large = (a1 - a0) > Math.PI ? 1 : 0
    const d = `M ${x0} ${y0} A 6 6 0 ${large} 1 ${x1} ${y1} L ${x2} ${y2} A ${r} ${r} 0 ${large} 0 ${x3} ${y3} Z`
    const heat = count / maxCount.value
    const ci = Math.min(Math.floor(heat * COLORS.length), COLORS.length - 1)
    return { d, color: COLORS[ci] }
  })
})

const hourLabels = computed(() => {
  return [0, 6, 12, 18].map(h => {
    const angle = (h / 24) * TAU
    const r = maxR + 14
    return {
      h,
      x: polarX(angle, r),
      y: polarY(angle, r),
      text: h === 0 ? '0h' : `${h}h`,
    }
  })
})
</script>

<style scoped>
.polar-wrap { display: flex; flex-direction: column; gap: 8px; padding: 20px; }

.polar-title {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--text-dim);
}

.polar-svg { width: 100%; max-width: 200px; margin: 0 auto; display: block; overflow: visible; }

.hour-lbl {
  font-size: 9px;
  fill: rgba(255,255,255,0.3);
  font-family: var(--font-body);
}
</style>
