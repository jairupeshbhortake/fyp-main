import api from '@/utils/api'

export default {
  namespaced: true,
  state: () => ({
    overview: null,
    batteryHealth: [],
    anomalies: [],
    loadingOverview: false,
    loadingBattery: false,
    loadingAnomalies: false,
  }),

  mutations: {
    SET_OVERVIEW(state, overview) { state.overview = overview },
    SET_BATTERY(state, battery) { state.batteryHealth = battery },
    SET_ANOMALIES(state, anomalies) { state.anomalies = anomalies },
    SET_LOADING_OVERVIEW(state, val) { state.loadingOverview = val },
    SET_LOADING_BATTERY(state, val) { state.loadingBattery = val },
    SET_LOADING_ANOMALIES(state, val) { state.loadingAnomalies = val },
  },

  actions: {
    async fetchOverview({ commit }) {
      commit('SET_LOADING_OVERVIEW', true)
      try {
        const { data } = await api.get('/analytics/overview')
        commit('SET_OVERVIEW', data)
      } finally {
        commit('SET_LOADING_OVERVIEW', false)
      }
    },

    async fetchBatteryHealth({ commit }) {
      commit('SET_LOADING_BATTERY', true)
      try {
        const { data } = await api.get('/analytics/battery-health')
        commit('SET_BATTERY', data)
      } finally {
        commit('SET_LOADING_BATTERY', false)
      }
    },

    async fetchAnomalies({ commit }, flightId) {
      commit('SET_LOADING_ANOMALIES', true)
      try {
        const { data } = await api.get(`/analytics/flights/${flightId}/anomalies`)
        commit('SET_ANOMALIES', data)
      } finally {
        commit('SET_LOADING_ANOMALIES', false)
      }
    },
  },
}
