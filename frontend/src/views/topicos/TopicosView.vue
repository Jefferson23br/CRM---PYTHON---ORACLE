<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const topicos = ref([])
const clientes = ref([])
const loading = ref(true)
const erro = ref('')
const modalAberto = ref(false)
const form = ref(topicoVazio())

function topicoVazio() {
  return {
    titulo: '',
    descricao: '',
    categoria: 'vendas',
    status: 'aberto',
    prioridade: 'media',
    cliente_id: null,
  }
}

async function carregar() {
  loading.value = true
  try {
    const [t, c] = await Promise.all([
      api.get('/topicos', { params: { page_size: 100 } }),
      api.get('/clientes', { params: { page_size: 100 } }),
    ])
    topicos.value = t.data.items
    clientes.value = c.data.items
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar tópicos'
  } finally {
    loading.value = false
  }
}

function abrirNovo() {
  form.value = topicoVazio()
  modalAberto.value = true
}

async function salvar() {
  erro.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.cliente_id) payload.cliente_id = null
    const { data } = await api.post('/topicos', payload)
    modalAberto.value = false
    router.push(`/topicos/${data.id}`)
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao criar tópico'
  }
}

async function excluir(id) {
  if (!confirm('Excluir este tópico?')) return
  await api.delete(`/topicos/${id}`)
  await carregar()
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Tópicos CRM</h1>
        <p>Atendimentos, negociações e acompanhamentos</p>
      </div>
      <button class="btn btn-primary" @click="abrirNovo">+ Novo tópico</button>
    </div>

    <div v-if="erro && !modalAberto" class="alert alert-error">{{ erro }}</div>

    <div class="card table-wrap" v-if="!loading">
      <table v-if="topicos.length">
        <thead>
          <tr>
            <th>Título</th>
            <th>Categoria</th>
            <th>Status</th>
            <th>Prioridade</th>
            <th>Cliente</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in topicos" :key="t.id">
            <td>
              <router-link :to="`/topicos/${t.id}`"><strong>{{ t.titulo }}</strong></router-link>
            </td>
            <td>{{ t.categoria || '—' }}</td>
            <td><span :class="['badge', `badge-${t.status}`]">{{ t.status }}</span></td>
            <td>{{ t.prioridade }}</td>
            <td>{{ clientes.find(c => c.id === t.cliente_id)?.nome || '—' }}</td>
            <td class="actions">
              <router-link :to="`/topicos/${t.id}`" class="btn btn-sm btn-secondary">Abrir</router-link>
              <button class="btn btn-sm btn-danger" @click="excluir(t.id)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">Nenhum tópico cadastrado</div>
    </div>
    <div v-else class="empty-state">Carregando...</div>

    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Novo tópico</h2>
          <button class="btn btn-sm btn-secondary" @click="modalAberto = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="erro" class="alert alert-error">{{ erro }}</div>
          <div class="form-group">
            <label>Título *</label>
            <input v-model="form.titulo" required />
          </div>
          <div class="form-group">
            <label>Descrição</label>
            <textarea v-model="form.descricao" rows="3"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Categoria</label>
              <input v-model="form.categoria" placeholder="vendas, suporte..." />
            </div>
            <div class="form-group">
              <label>Prioridade</label>
              <select v-model="form.prioridade">
                <option value="baixa">Baixa</option>
                <option value="media">Média</option>
                <option value="alta">Alta</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Cliente</label>
            <select v-model="form.cliente_id">
              <option :value="null">— Nenhum —</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="modalAberto = false">Cancelar</button>
          <button class="btn btn-primary" @click="salvar">Criar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.actions {
  display: flex;
  gap: 0.5rem;
}
</style>
