<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="logo-icon">◈</div>
        <div class="logo-text">DRONEVAULT</div>
        <div class="logo-sub">// FLIGHT INTELLIGENCE PLATFORM</div>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div class="form-group">
          <label>USERNAME</label>
          <input v-model="form.username" type="text" placeholder="callsign" autocomplete="username" required />
        </div>
        <div class="form-group">
          <label>PASSWORD</label>
          <input v-model="form.password" type="password" placeholder="••••••••" autocomplete="current-password" required />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'AUTHENTICATING...' : 'LOGIN →' }}
        </button>
      </form>

      <div class="register-link">
        No account?
        <a href="#" @click.prevent="showRegister = !showRegister">Register</a>
      </div>

      <form v-if="showRegister" class="login-form register-form" @submit.prevent="register">
        <div class="form-group">
          <label>EMAIL</label>
          <input v-model="reg.email" type="email" placeholder="pilot@example.com" required />
        </div>
        <div class="form-group">
          <label>USERNAME</label>
          <input v-model="reg.username" type="text" placeholder="callsign" required />
        </div>
        <div class="form-group">
          <label>PASSWORD</label>
          <input v-model="reg.password" type="password" placeholder="••••••••" required />
        </div>
        <p v-if="regError" class="error-msg">{{ regError }}</p>
        <button type="submit" class="login-btn" :disabled="regLoading">
          {{ regLoading ? 'CREATING...' : 'CREATE ACCOUNT →' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store  = useStore()
const router = useRouter()

const form    = reactive({ username: '', password: '' })
const error   = ref('')
const loading = ref(false)

const showRegister = ref(false)
const reg       = reactive({ email: '', username: '', password: '' })
const regError  = ref('')
const regLoading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await store.dispatch('auth/login', { username: form.username, password: form.password })
    router.push('/')
  } catch (e) {
    error.value = e.message || 'Authentication failed'
  } finally {
    loading.value = false
  }
}

async function register() {
  regError.value = ''
  regLoading.value = true
  try {
    await store.dispatch('auth/register', { ...reg })
    showRegister.value = false
    Object.assign(form, { username: reg.username, password: reg.password })
    await submit()
  } catch (e) {
    regError.value = e.message || 'Registration failed'
  } finally {
    regLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-dark);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 40px 32px;
}

.login-logo {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  font-size: 36px;
  color: var(--amber);
  line-height: 1;
  margin-bottom: 8px;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 6px;
  color: var(--amber-bright);
}

.logo-sub {
  font-size: 10px;
  letter-spacing: 2px;
  color: var(--text-faint);
  margin-top: 4px;
}

.login-form { display: flex; flex-direction: column; gap: 16px; }
.register-form { margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--border); }

.form-group { display: flex; flex-direction: column; gap: 5px; }

.form-group label {
  font-size: 9px;
  letter-spacing: 2px;
  color: var(--text-faint);
  text-transform: uppercase;
}

.form-group input {
  background: var(--bg-dark);
  border: 1px solid var(--border);
  color: var(--amber);
  font-family: var(--font-mono);
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 2px;
  outline: none;
  transition: border-color 0.15s;
}

.form-group input:focus { border-color: var(--amber); }
.form-group input::placeholder { color: var(--text-faint); }

.error-msg {
  font-size: 11px;
  color: #f87171;
  letter-spacing: 0.5px;
}

.login-btn {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 2px;
  padding: 10px;
  border: 1px solid var(--amber);
  background: var(--amber-glow);
  color: var(--amber-bright);
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
  margin-top: 4px;
}

.login-btn:hover:not(:disabled) { background: rgba(245,158,11,0.25); }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.register-link {
  text-align: center;
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 20px;
}

.register-link a { color: var(--amber); cursor: pointer; }
</style>
