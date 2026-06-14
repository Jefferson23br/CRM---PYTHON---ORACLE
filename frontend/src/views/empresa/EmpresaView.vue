<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()
const empresa = ref(null)
const loading = ref(true)
const erro = ref('')
const sucesso = ref('')
const form = ref({})

async function carregar() {
  if (!auth.usuario?.empresa_id) {
    loading.value = false
    return
  }
  try {
    const { data } = await api.get(`/empresas/${auth.usuario.empresa_id}`)
    empresa.value = data
    form.value = { ...data }
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar empresa'
  } finally {
    loading.value = false
  }
}

async function salvar() {
  erro.value = ''
  sucesso.value = ''
  try {
    const payload = {
      razao_social: form.value.razao_social,
      nome_fantasia: form.value.nome_fantasia,
      email: form.value.email,
      telefone: form.value.telefone,
      endereco: form.value.endereco,
      cidade: form.value.cidade,
      estado: form.value.estado,
      cep: form.value.cep,
    }
    const { data } = await api.put(`/empresas/${auth.usuario.empresa_id}`, payload)
    empresa.value = data
    sucesso.value = 'Empresa atualizada com sucesso'
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar'
  }
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Empresa</h1>
        <p>Dados da sua organização</p>
      </div>
    </div>

    <div v-if="erro" class="alert alert-error">{{ erro }}</div>
    <div v-if="sucesso" class="alert alert-success">{{ sucesso }}</div>

    <div v-if="loading" class="empty-state">Carregando...</div>

    <div v-else-if="empresa" class="card form-card">
      <form @submit.prevent="salvar">
        <div class="form-group">
          <label>Razão social</label>
          <input v-model="form.razao_social" required />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Nome fantasia</label>
            <input v-model="form.nome_fantasia" />
          </div>
          <div class="form-group">
            <label>CNPJ</label>
            <input v-model="form.cnpj" disabled />
          </div>
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
        <div class="form-group">
          <label>Endereço</label>
          <input v-model="form.endereco" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Cidade</label>
            <input v-model="form.cidade" />
          </div>
          <div class="form-group">
            <label>Estado</label>
            <input v-model="form.estado" maxlength="2" />
          </div>
          <div class="form-group">
            <label>CEP</label>
            <input v-model="form.cep" />
          </div>
        </div>
        <div class="form-footer">
          <span class="status-info">Status: <strong>{{ empresa.status }}</strong></span>
          <button type="submit" class="btn btn-primary">Salvar alterações</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.form-card {
  padding: 1.5rem;
  max-width: 720px;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.status-info {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}
</style>
