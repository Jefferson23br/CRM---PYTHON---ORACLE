<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const erro = ref('')
const form = ref({
  empresa: {
    razao_social: '',
    nome_fantasia: '',
    cnpj: '',
    email: '',
  },
  usuario: {
    nome: '',
    email: '',
    senha: '',
    telefone: '',
  },
})

async function enviar() {
  erro.value = ''
  try {
    await auth.registro(form.value.empresa, form.value.usuario)
    router.push('/')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao registrar. Verifique os dados.'
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <h1>Criar conta</h1>
        <p>Registre sua empresa e usuário administrador</p>
      </div>

      <div v-if="erro" class="alert alert-error">{{ erro }}</div>

      <form @submit.prevent="enviar">
        <h3 class="section-title">Empresa</h3>
        <div class="form-group">
          <label>Razão social *</label>
          <input v-model="form.empresa.razao_social" required />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Nome fantasia</label>
            <input v-model="form.empresa.nome_fantasia" />
          </div>
          <div class="form-group">
            <label>CNPJ *</label>
            <input v-model="form.empresa.cnpj" required placeholder="00.000.000/0000-00" />
          </div>
        </div>
        <div class="form-group">
          <label>E-mail da empresa</label>
          <input v-model="form.empresa.email" type="email" />
        </div>

        <h3 class="section-title">Administrador</h3>
        <div class="form-group">
          <label>Nome *</label>
          <input v-model="form.usuario.nome" required />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>E-mail *</label>
            <input v-model="form.usuario.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Telefone</label>
            <input v-model="form.usuario.telefone" />
          </div>
        </div>
        <div class="form-group">
          <label>Senha * (mín. 8 caracteres)</label>
          <input v-model="form.usuario.senha" type="password" required minlength="8" />
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="auth.loading">
          {{ auth.loading ? 'Criando...' : 'Criar conta' }}
        </button>
      </form>

      <div class="auth-links">
        <router-link to="/login">Já tenho conta</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #2563eb 100%);
}

.auth-card {
  width: 100%;
  max-width: 560px;
  padding: 2rem;
  max-height: 95vh;
  overflow-y: auto;
}

.auth-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.auth-header h1 {
  font-size: 1.5rem;
}

.auth-header p {
  color: var(--color-text-muted);
}

.section-title {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary);
  margin: 1rem 0 0.75rem;
}

.btn-block {
  width: 100%;
  margin-top: 0.5rem;
}

.auth-links {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
}
</style>
