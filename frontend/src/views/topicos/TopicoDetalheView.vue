<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const topico = ref(null)
const mensagens = ref([])
const novaMensagem = ref('')
const loading = ref(true)
const erro = ref('')

async function carregar() {
  loading.value = true
  const id = route.params.id
  try {
    const [t, m] = await Promise.all([
      api.get(`/topicos/${id}`),
      api.get(`/topicos/${id}/mensagens`, { params: { page_size: 100 } }),
    ])
    topico.value = t.data
    mensagens.value = m.data.items
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar tópico'
  } finally {
    loading.value = false
  }
}

async function enviarMensagem() {
  if (!novaMensagem.value.trim()) return
  await api.post(`/topicos/${route.params.id}/mensagens`, {
    conteudo: novaMensagem.value,
    tipo: 'texto',
  })
  novaMensagem.value = ''
  const { data } = await api.get(`/topicos/${route.params.id}/mensagens`, {
    params: { page_size: 100 },
  })
  mensagens.value = data.items
}

async function atualizarStatus(status) {
  await api.put(`/topicos/${route.params.id}`, { status })
  topico.value.status = status
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/topicos" class="back-link">← Voltar</router-link>
        <h1 v-if="topico">{{ topico.titulo }}</h1>
        <p v-if="topico">
          <span :class="['badge', `badge-${topico.status}`]">{{ topico.status }}</span>
          · {{ topico.prioridade }} · {{ topico.categoria || 'sem categoria' }}
        </p>
      </div>
      <div v-if="topico" class="status-actions">
        <select :value="topico.status" @change="atualizarStatus($event.target.value)">
          <option value="aberto">Aberto</option>
          <option value="em_andamento">Em andamento</option>
          <option value="resolvido">Resolvido</option>
          <option value="fechado">Fechado</option>
        </select>
      </div>
    </div>

    <div v-if="erro" class="alert alert-error">{{ erro }}</div>
    <div v-if="loading" class="empty-state">Carregando...</div>

    <template v-else-if="topico">
      <div class="card descricao" v-if="topico.descricao">
        <p>{{ topico.descricao }}</p>
      </div>

      <div class="card mensagens-box">
        <h2>Mensagens</h2>
        <div class="mensagens-lista">
          <div v-for="m in mensagens" :key="m.id" class="mensagem-item">
            <div class="mensagem-meta">#{{ m.id }} · {{ new Date(m.criado_em).toLocaleString('pt-BR') }}</div>
            <p>{{ m.conteudo }}</p>
          </div>
          <div v-if="!mensagens.length" class="empty-state">Nenhuma mensagem ainda</div>
        </div>
        <form class="nova-mensagem" @submit.prevent="enviarMensagem">
          <textarea v-model="novaMensagem" rows="3" placeholder="Escreva uma mensagem..." required></textarea>
          <button type="submit" class="btn btn-primary">Enviar</button>
        </form>
      </div>
    </template>
  </div>
</template>

<style scoped>
.back-link {
  font-size: 0.875rem;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.status-actions select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.descricao {
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  color: var(--color-text-muted);
}

.mensagens-box {
  padding: 1.25rem;
}

.mensagens-box h2 {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.mensagens-lista {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.mensagem-item {
  padding: 0.875rem;
  background: #f8fafc;
  border-radius: var(--radius);
  margin-bottom: 0.75rem;
}

.mensagem-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.25rem;
}

.nova-mensagem {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.nova-mensagem textarea {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  resize: vertical;
}
</style>
