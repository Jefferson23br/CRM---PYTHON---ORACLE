<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const clientes = ref([])
const loading = ref(true)
const busca = ref('')
const erro = ref('')
const modalAberto = ref(false)
const editando = ref(null)
const form = ref(clienteVazio())

function clienteVazio() {
  return {
    nome: '',
    email: '',
    telefone: '',
    celular: '',
    cpf_cnpj: '',
    status: 'prospecto',
    origem: '',
    observacoes: '',
  }
}

async function carregar() {
  loading.value = true
  try {
    const { data } = await api.get('/clientes', {
      params: { busca: busca.value || undefined, page_size: 100 },
    })
    clientes.value = data.items
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar clientes'
  } finally {
    loading.value = false
  }
}

function abrirNovo() {
  editando.value = null
  form.value = clienteVazio()
  modalAberto.value = true
}

function abrirEditar(cliente) {
  editando.value = cliente.id
  form.value = { ...cliente }
  modalAberto.value = true
}

async function salvar() {
  erro.value = ''
  try {
    if (editando.value) {
      await api.put(`/clientes/${editando.value}`, form.value)
    } else {
      await api.post('/clientes', form.value)
    }
    modalAberto.value = false
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar cliente'
  }
}

async function excluir(id) {
  if (!confirm('Excluir este cliente?')) return
  await api.delete(`/clientes/${id}`)
  await carregar()
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Clientes</h1>
        <p>Cadastro de leads, prospectos e clientes</p>
      </div>
      <button class="btn btn-primary" @click="abrirNovo">+ Novo cliente</button>
    </div>

    <div class="card toolbar">
      <input
        v-model="busca"
        type="search"
        placeholder="Buscar por nome, e-mail ou telefone..."
        @keyup.enter="carregar"
      />
      <button class="btn btn-secondary" @click="carregar">Buscar</button>
    </div>

    <div v-if="erro && !modalAberto" class="alert alert-error">{{ erro }}</div>

    <div class="card table-wrap" v-if="!loading">
      <table v-if="clientes.length">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Telefone</th>
            <th>Status</th>
            <th>Origem</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in clientes" :key="c.id">
            <td><strong>{{ c.nome }}</strong></td>
            <td>{{ c.email || '—' }}</td>
            <td>{{ c.telefone || c.celular || '—' }}</td>
            <td><span :class="['badge', `badge-${c.status}`]">{{ c.status }}</span></td>
            <td>{{ c.origem || '—' }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" @click="abrirEditar(c)">Editar</button>
              <button class="btn btn-sm btn-danger" @click="excluir(c.id)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">Nenhum cliente cadastrado</div>
    </div>
    <div v-else class="empty-state">Carregando...</div>

    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editando ? 'Editar cliente' : 'Novo cliente' }}</h2>
          <button class="btn btn-sm btn-secondary" @click="modalAberto = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="erro" class="alert alert-error">{{ erro }}</div>
          <div class="form-group">
            <label>Nome *</label>
            <input v-model="form.nome" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>E-mail</label>
              <input v-model="form.email" type="email" />
            </div>
            <div class="form-group">
              <label>Telefone</label>
              <input v-model="form.telefone" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="form.status">
                <option value="lead">Lead</option>
                <option value="prospecto">Prospecto</option>
                <option value="ativo">Ativo</option>
                <option value="inativo">Inativo</option>
              </select>
            </div>
            <div class="form-group">
              <label>Origem</label>
              <input v-model="form.origem" placeholder="facebook, google_ads..." />
            </div>
          </div>
          <div class="form-group">
            <label>Observações</label>
            <textarea v-model="form.observacoes" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="modalAberto = false">Cancelar</button>
          <button class="btn btn-primary" @click="salvar">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.toolbar input {
  flex: 1;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.actions {
  display: flex;
  gap: 0.5rem;
  white-space: nowrap;
}
</style>
