<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()
const stats = ref({ clientes: 0, topicos: 0, usuarios: 0, topicosAbertos: 0 })
const loading = ref(true)

onMounted(async () => {
  try {
    const [clientes, topicos, usuarios] = await Promise.all([
      api.get('/clientes', { params: { page_size: 1 } }),
      api.get('/topicos', { params: { page_size: 1 } }),
      api.get('/usuarios', { params: { page_size: 1 } }),
    ])
    const topicosAbertos = await api.get('/topicos', {
      params: { status: 'aberto', page_size: 1 },
    })
    stats.value = {
      clientes: clientes.data.total,
      topicos: topicos.data.total,
      usuarios: usuarios.data.total,
      topicosAbertos: topicosAbertos.data.total,
    }
  } catch {
    /* dashboard carrega parcialmente se alguma rota falhar */
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p>Bem-vindo, {{ auth.usuario?.nome }}</p>
      </div>
    </div>

    <div class="stats-grid" v-if="!loading">
      <div class="stat-card card">
        <span class="stat-icon">👥</span>
        <div>
          <strong>{{ stats.clientes }}</strong>
          <span>Clientes</span>
        </div>
      </div>
      <div class="stat-card card">
        <span class="stat-icon">💬</span>
        <div>
          <strong>{{ stats.topicos }}</strong>
          <span>Tópicos CRM</span>
        </div>
      </div>
      <div class="stat-card card">
        <span class="stat-icon">📂</span>
        <div>
          <strong>{{ stats.topicosAbertos }}</strong>
          <span>Tópicos abertos</span>
        </div>
      </div>
      <div class="stat-card card">
        <span class="stat-icon">🔐</span>
        <div>
          <strong>{{ stats.usuarios }}</strong>
          <span>Usuários</span>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">Carregando...</div>

    <div class="info-card card">
      <h2>CRM Piloto</h2>
      <p>
        Sistema multi-empresa para gestão de clientes, leads e funil de vendas.
        Integrações futuras com Facebook (Meta) e Google Ads.
      </p>
      <div class="quick-links">
        <router-link to="/clientes" class="btn btn-secondary">Gerenciar clientes</router-link>
        <router-link to="/topicos" class="btn btn-secondary">Ver tópicos</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
}

.stat-icon {
  font-size: 2rem;
}

.stat-card strong {
  display: block;
  font-size: 1.75rem;
  line-height: 1.2;
}

.stat-card span {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.info-card {
  padding: 1.5rem;
}

.info-card h2 {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.info-card p {
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}

.quick-links {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
</style>
