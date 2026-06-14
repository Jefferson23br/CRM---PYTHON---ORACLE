<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const usuarios = ref([])
const loading = ref(true)
const erro = ref('')
const modalAberto = ref(false)
const editando = ref(null)
const form = ref(usuarioVazio())

const tipos = [
  { value: 'admin_empresa', label: 'Admin empresa' },
  { value: 'gerente', label: 'Gerente' },
  { value: 'vendedor', label: 'Vendedor' },
  { value: 'atendente', label: 'Atendente' },
  { value: 'visualizador', label: 'Visualizador' },
]

function usuarioVazio() {
  return {
    nome: '',
    email: '',
    senha: '',
    telefone: '',
    cargo: '',
    tipo: 'vendedor',
    ativo: true,
  }
}

async function carregar() {
  loading.value = true
  try {
    const { data } = await api.get('/usuarios', { params: { page_size: 100 } })
    usuarios.value = data.items
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar usuários'
  } finally {
    loading.value = false
  }
}

function abrirNovo() {
  editando.value = null
  form.value = usuarioVazio()
  modalAberto.value = true
}

function abrirEditar(u) {
  editando.value = u.id
  form.value = { ...u, senha: '' }
  modalAberto.value = true
}

async function salvar() {
  erro.value = ''
  try {
    if (editando.value) {
      const payload = { ...form.value }
      delete payload.senha
      delete payload.id
      delete payload.empresa_id
      delete payload.criado_em
      delete payload.atualizado_em
      delete payload.ultimo_acesso
      delete payload.email_verificado
      await api.put(`/usuarios/${editando.value}`, payload)
    } else {
      await api.post('/usuarios', form.value)
    }
    modalAberto.value = false
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar usuário'
  }
}

async function excluir(id) {
  if (!confirm('Excluir este usuário?')) return
  await api.delete(`/usuarios/${id}`)
  await carregar()
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Usuários</h1>
        <p>Gerencie a equipe da sua empresa</p>
      </div>
      <button class="btn btn-primary" @click="abrirNovo">+ Novo usuário</button>
    </div>

    <div v-if="erro && !modalAberto" class="alert alert-error">{{ erro }}</div>

    <div class="card table-wrap" v-if="!loading">
      <table v-if="usuarios.length">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Tipo</th>
            <th>Cargo</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id">
            <td><strong>{{ u.nome }}</strong></td>
            <td>{{ u.email }}</td>
            <td>{{ u.tipo }}</td>
            <td>{{ u.cargo || '—' }}</td>
            <td>{{ u.ativo ? 'Ativo' : 'Inativo' }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" @click="abrirEditar(u)">Editar</button>
              <button class="btn btn-sm btn-danger" @click="excluir(u.id)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">Nenhum usuário cadastrado</div>
    </div>
    <div v-else class="empty-state">Carregando...</div>

    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editando ? 'Editar usuário' : 'Novo usuário' }}</h2>
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
              <label>E-mail *</label>
              <input v-model="form.email" type="email" required :disabled="!!editando" />
            </div>
            <div class="form-group">
              <label>Tipo</label>
              <select v-model="form.tipo">
                <option v-for="t in tipos" :key="t.value" :value="t.value">{{ t.label }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Cargo</label>
              <input v-model="form.cargo" />
            </div>
            <div class="form-group">
              <label>Telefone</label>
              <input v-model="form.telefone" />
            </div>
          </div>
          <div class="form-group" v-if="!editando">
            <label>Senha *</label>
            <input v-model="form.senha" type="password" required minlength="8" />
          </div>
          <div class="form-group" v-if="editando">
            <label>
              <input type="checkbox" v-model="form.ativo" /> Usuário ativo
            </label>
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
.actions {
  display: flex;
  gap: 0.5rem;
}
</style>
