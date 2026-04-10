<template>
  <div class="spinner-wrap" :class="{ overlay: overlay }">
    <div class="spinner">
      <svg viewBox="0 0 50 50" class="spin-svg">
        <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="3"
          stroke-dasharray="94 32" stroke-linecap="round" />
      </svg>
    </div>
    <p v-if="label" class="spin-label">{{ label }}</p>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  overlay: { type: Boolean, default: false },
})
</script>

<style scoped>
.spinner-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 14px;
}

.spinner-wrap.overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 6, 0.7);
  z-index: 50;
}

.spinner { width: 36px; height: 36px; color: var(--amber); }

.spin-svg { animation: rotate 1.2s linear infinite; }

@keyframes rotate { to { transform: rotate(360deg); } }

.spin-label {
  font-size: 10px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--text-dim);
}
</style>
