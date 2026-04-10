import api from '@/utils/api'

export default {
  namespaced: true,
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: () => true,
  },

  mutations: {
    SET_LOADING(state, loading) { state.loading = loading },
    SET_ERROR(state, error) { state.error = error },
    SET_TOKEN(state, token) { state.token = token; if(token) localStorage.setItem('token', token); else localStorage.removeItem('token') },
    SET_USER(state, user) { state.user = user },
  },

  actions: {
    async login({ commit, dispatch }, { username, password }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const params = new URLSearchParams({ username, password })
        const { data } = await api.post('/auth/token', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        commit('SET_TOKEN', data.access_token)
        await dispatch('fetchMe')
      } catch (e) {
        commit('SET_ERROR', e.response?.data?.detail || 'Login failed')
        throw e
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async register({ commit, dispatch }, { email, username, password }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        await api.post('/auth/register', { email, username, password })
        await dispatch('login', { username, password })
      } catch (e) {
        commit('SET_ERROR', e.response?.data?.detail || 'Registration failed')
        throw e
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchMe({ commit, dispatch }) {
      try {
        const { data } = await api.get('/auth/me')
        commit('SET_USER', data)
      } catch {
        dispatch('logout')
      }
    },

    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
    },
  },
}
