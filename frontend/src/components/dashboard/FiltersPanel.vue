<template>
  <div class="filters-panel">
    <div class="filters-header">
      <span class="section-label">// filter</span>
      <button v-if="hasActiveFilters" class="clear-btn" @click="clearFilters">CLEAR</button>
    </div>

    <div class="filter-group">
      <label class="filter-label">DRONE MODEL</label>
      <select class="filter-select" v-model="filters.drone" @change="apply">
        <option value="">ALL UNITS</option>
        <option v-for="d in drones" :key="d" :value="d">{{ d }}</option>
      </select>
    </div>

    <div class="filter-group">
      <label class="filter-label">SOURCE</label>
      <select class="filter-select" v-model="filters.source" @change="apply">
        <option value="">ALL SOURCES</option>
        <option value="DJI">DJI</option>
        <option value="LITCHI">LITCHI</option>
        <option value="MANUAL">MANUAL</option>
      </select>
    </div>

    <div class="filter-group">
      <label class="filter-label">DATE FROM</label>
      <input type="date" class="filter-input" v-model="filters.dateFrom" @change="apply" />
    </div>

    <div class="filter-group">
      <label class="filter-label">DATE TO</label>
      <input type="date" class="filter-input" v-model="filters.dateTo" @change="apply" />
    </div>

    <div class="filter-group">
      <label class="filter-label">MIN DURATION</label>
      <div class="slider-row">
        <input type="range" min="0" max="120" step="5"
          v-model.number="filters.minDuration" @input="apply" />
        <span class="slider-val">{{ filters.minDuration }}min</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const filters = reactive({
  drone: '',
  source: '',
  dateFrom: '',
  dateTo: '',
  minDuration: 0,
})

const drones = computed(() => store.getters['flights/droneModels'])

const hasActiveFilters = computed(() =>
  filters.drone || filters.source || filters.dateFrom || filters.dateTo || filters.minDuration > 0
)

function apply() {
  store.commit('flights/SET_FILTERS', { ...filters })
}

function clearFilters() {
  Object.assign(filters, { drone: '', source: '', dateFrom: '', dateTo: '', minDuration: 0 })
  apply()
}
</script>

<style scoped>
.filters-panel { padding: 4px 0 12px; border-bottom: 1px solid var(--border); }

.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px 4px;
}

.section-label { font-size: 10px; letter-spacing: 3px; color: var(--text-faint); text-transform: uppercase; }

.clear-btn {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 1px;
  padding: 3px 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  border-radius: 2px;
}

.clear-btn:hover { border-color: var(--amber); color: var(--amber); }

.filter-group { padding: 5px 14px; }

.filter-label {
  display: block;
  font-size: 9px;
  letter-spacing: 2px;
  color: var(--text-faint);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.filter-select,
.filter-input {
  width: 100%;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 2px;
  outline: none;
}

.filter-select:focus,
.filter-input:focus { border-color: var(--border-hover); color: var(--amber); }

.filter-select option { background: var(--bg-panel); }

.filter-input::-webkit-calendar-picker-indicator {
  filter: invert(0.6) sepia(1) saturate(4) hue-rotate(10deg);
}

.slider-row { display: flex; align-items: center; gap: 10px; }
.slider-row input[type=range] { flex: 1; accent-color: var(--amber); }
.slider-val { font-size: 10px; color: var(--text-dim); min-width: 36px; text-align: right; }
</style>
