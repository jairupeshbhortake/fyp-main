import { createStore } from 'vuex'
import auth from './modules/auth'
import flights from './modules/flights'
import analytics from './modules/analytics'

export default createStore({
  modules: { auth, flights, analytics },
  strict: import.meta.env.DEV,
})
