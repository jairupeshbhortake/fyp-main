<template>
  <div id="dronevault-app">
    <NavBar v-if="isAuthenticated" />
    <main class="main-content" :class="{ 'with-nav': isAuthenticated }">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import NavBar from './components/common/NavBar.vue'

const store = useStore()
const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
</script>

<style>
/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.main-content {
  min-height: 100vh;
}

.main-content.with-nav {
  padding-top: var(--topbar-h);
}
</style>
