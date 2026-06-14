<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const menu = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/clientes', label: 'Clientes', icon: '👥' },
  { to: '/topicos', label: 'Tópicos CRM', icon: '💬' },
  { to: '/usuarios', label: 'Usuários', icon: '🔐' },
  { to: '/empresa', label: 'Empresa', icon: '🏢' },
]

function sair() {
  auth.logout()
  router.replace({ name: 'login' })
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="brand-icon">C</span>
      <div>
        <strong>CRM Piloto</strong>
        <small>Gestão de vendas</small>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in menu"
        :key="item.to"
        :to="item.to"
        class="nav-link"
        :class="{ active: $route.path === item.to || ($route.path.startsWith(item.to) && item.to !== '/') }"
      >
        <span>{{ item.icon }}</span>
        {{ item.label }}
      </router-link>
    </nav>

    <div class="sidebar-footer" v-if="auth.usuario">
      <div class="user-info">
        <strong>{{ auth.usuario.nome }}</strong>
        <small>{{ auth.usuario.tipo }}</small>
      </div>
      <button class="btn btn-sm btn-secondary" @click="sair">Sair</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  background: var(--color-sidebar);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  border-bottom: 1px solid #1e293b;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: var(--color-primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: white;
}

.sidebar-brand strong {
  display: block;
  color: white;
}

.sidebar-brand small {
  color: #94a3b8;
  font-size: 0.75rem;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.15s;
}

.nav-link:hover {
  background: var(--color-sidebar-hover);
  text-decoration: none;
  color: white;
}

.nav-link.active {
  background: var(--color-primary);
  color: white;
}

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #1e293b;
}

.user-info {
  margin-bottom: 0.75rem;
}

.user-info strong {
  display: block;
  color: white;
  font-size: 0.9rem;
}

.user-info small {
  color: #94a3b8;
  text-transform: capitalize;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
  }

  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
    overflow-x: auto;
  }
}
</style>
