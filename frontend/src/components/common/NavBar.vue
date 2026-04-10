<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <img src="../../assets/logo.svg" alt="DroneVault" class="logo" />
      <span class="brand-name">DRONEVAULT</span>
    </div>

    <div class="navbar-links">
      <router-link to="/" class="nav-link" active-class="active">
        <span class="icon">⬡</span> Dashboard
      </router-link>
      <router-link to="/analytics" class="nav-link" active-class="active">
        <span class="icon">◈</span> Analytics
      </router-link>
      <router-link to="/battery" class="nav-link" active-class="active">
        <span class="icon">▣</span> Battery
      </router-link>
    </div>

    <div class="navbar-right">
      <span class="username">{{ username }}</span>
      <button class="btn-logout theme-toggle" @click="toggleTheme" style="margin-right: 8px;" :title="isLight ? 'Switch to Dark Mode' : 'Switch to Light Mode'">
        {{ isLight ? '🌙' : '☀️' }}
      </button>
      <button class="btn-logout" @click="resetApp" style="margin-right: 8px;">RESET</button>
      <button class="btn-logout" @click="logout">LOGOUT</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()
const username = computed(() => store.state.auth.user?.username || '')

function logout() {
  store.dispatch('auth/logout')
  router.push('/login')
}

function resetApp() {
  if (confirm('This will delete all flights and reset your analytics. Are you sure?')) {
    store.dispatch('flights/deleteAllFlights')
  }
}

const isLight = ref(false)

function toggleTheme() {
  isLight.value = !isLight.value
  if (isLight.value) {
    document.documentElement.classList.add('theme-light')
    localStorage.setItem('theme', 'light')
  } else {
    document.documentElement.classList.remove('theme-light')
    localStorage.setItem('theme', 'dark')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'light') {
    isLight.value = true
    document.documentElement.classList.add('theme-light')
  }
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--topbar-h);
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  padding: 0 32px;
  gap: 32px;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo { width: 32px; height: 32px; filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.4)); }

.brand-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 2px;
  background: linear-gradient(to right, var(--text-main), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.navbar-links {
  display: flex;
  gap: 8px;
  flex: 1;
  margin-left: 16px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-dim);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.nav-link:hover { color: var(--text-main); background: rgba(255,255,255,0.05); }
.nav-link.active { 
  color: var(--accent-cyan); 
  background: rgba(0, 242, 254, 0.1); 
  box-shadow: inset 0 -2px 0 var(--accent-cyan);
}

.icon { font-size: 14px; }

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
}

.username { 
  font-size: 13px; 
  font-weight: 500;
  color: var(--text-dim); 
}

.btn-logout {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  padding: 6px 14px;
  border: 1px solid var(--glass-border);
  background: rgba(255,255,255,0.05);
  color: var(--text-dim);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.btn-logout:hover { border-color: var(--red); color: var(--red); background: rgba(239, 68, 68, 0.1); }
.theme-toggle:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); background: rgba(0, 242, 254, 0.1); }
</style>
