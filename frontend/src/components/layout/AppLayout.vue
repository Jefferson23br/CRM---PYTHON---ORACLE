<script setup>
import AppSidebar from './AppSidebar.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-x: hidden;
}

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .app-main {
    padding: 1rem;
  }
}
</style>
