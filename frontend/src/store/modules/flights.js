import api from '@/utils/api'

export default {
  namespaced: true,
  state: () => ({
    flights: [],
    selectedFlight: null,
    loading: false,
    uploading: false,
    error: null,
    filters: {
      drone: 'ALL',
      source: 'ALL',
      dateFrom: null,
      dateTo: null,
    },
  }),

  getters: {
    filteredFlights: (state) => {
      return state.flights.filter((f) => {
        if (state.filters.drone !== 'ALL' && f.drone_model !== state.filters.drone) return false
        if (state.filters.source !== 'ALL' && f.source !== state.filters.source) return false
        if (state.filters.dateFrom && f.date < state.filters.dateFrom) return false
        if (state.filters.dateTo && f.date > state.filters.dateTo + 'T23:59:59Z') return false
        return true
      })
    },
    // Alias used by HeatmapLayer and other components
    list: (state) => state.flights,
  },

  mutations: {
    SET_LOADING(state, val) { state.loading = val },
    SET_UPLOADING(state, val) { state.uploading = val },
    SET_ERROR(state, err) { state.error = err },
    SET_FLIGHTS(state, flights) { state.flights = flights },
    SET_SELECTED_FLIGHT(state, flight) { state.selectedFlight = flight },
    ADD_FLIGHT(state, flight) { state.flights.unshift(flight) },
    REMOVE_FLIGHT(state, id) { state.flights = state.flights.filter((f) => f.id !== id) },
    SET_FILTER(state, patch) { state.filters = { ...state.filters, ...patch } },
    CLEAR_FILTERS(state) { state.filters = { drone: 'ALL', source: 'ALL', dateFrom: null, dateTo: null } },
  },

  actions: {
    async fetchAll({ dispatch }) {
      return dispatch('fetchFlights')
    },

    async fetchFlights({ commit, state }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const { data } = await api.get('/flights')
        commit('SET_FLIGHTS', data)
        if (data.length && !state.selectedFlight) {
          commit('SET_SELECTED_FLIGHT', data[0])
        }
      } catch (e) {
        commit('SET_ERROR', e.response?.data?.detail || 'Failed to fetch flights')
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async selectFlight({ commit }, flightId) {
      try {
        const { data } = await api.get(`/flights/${flightId}`)
        commit('SET_SELECTED_FLIGHT', data)
      } catch (e) {
        commit('SET_ERROR', 'Failed to load flight detail')
      }
    },

    async upload({ commit, state }, file) {
      commit('SET_UPLOADING', true)
      commit('SET_ERROR', null)
      try {
        const form = new FormData()
        form.append('file', file)
        const { data } = await api.post('/flights/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        commit('ADD_FLIGHT', data)
        commit('SET_SELECTED_FLIGHT', data)
        return data
      } catch (e) {
        commit('SET_ERROR', e.response?.data?.detail || 'Upload failed')
        throw e
      } finally {
        commit('SET_UPLOADING', false)
      }
    },

    async deleteFlight({ commit, state }, flightId) {
      try {
        await api.delete(`/flights/${flightId}`)
        commit('REMOVE_FLIGHT', flightId)
        if (state.selectedFlight?.id === flightId) {
          commit('SET_SELECTED_FLIGHT', state.flights[0] || null)
        }
      } catch (e) {
        commit('SET_ERROR', 'Failed to delete flight')
      }
    },

    async deleteAllFlights({ commit, dispatch }) {
      try {
        await api.delete('/flights')
        commit('SET_FLIGHTS', [])
        commit('SET_SELECTED_FLIGHT', null)
        dispatch('analytics/fetchOverview', null, { root: true })
      } catch (e) {
        commit('SET_ERROR', 'Failed to delete all flights')
      }
    },

    setFilter({ commit }, patch) {
      commit('SET_FILTER', patch)
    },

    clearFilters({ commit }) {
      commit('CLEAR_FILTERS')
    },
  },
}
