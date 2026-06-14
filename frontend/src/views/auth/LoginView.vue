<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const senha = ref('')
const erro = ref('')

async function enviar() {
  erro.value = ''
  try {
    await auth.login(email.value, senha.value)
    await router.replace({ name: 'dashboard' })
  } catch (e) {
    if (!e.response) {
      erro.value = 'Erro de conexão com a API. Verifique CORS e a URL da API.'
    } else {
      erro.value = e.response?.data?.detail || 'E-mail ou senha incorretos'
    }
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <span class="logo">C</span>
        <h1>CRM Piloto</h1>
        <p>Entre na sua conta</p>
      </div>

      <div v-if="erro" class="alert alert-error">{{ erro }}</div>

      <form @submit.prevent="enviar">
        <div class="form-group">
          <label>E-mail</label>
          <input v-model="email" type="email" required placeholder="seu@email.com" />
        </div>
        <div class="form-group">
          <label>Senha</label>
          <input v-model="senha" type="password" required placeholder="••••••••" />
        </div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="auth.loading">
          {{ auth.loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <div class="auth-links">
        <router-link to="/recuperar-senha">Esqueci minha senha</router-link>
        <router-link to="/registro">Criar conta / empresa</router-link>
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
  max-width: 420px;
  padding: 2rem;
}

.auth-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.logo {
  display: inline-flex;
  width: 48px;
  height: 48px;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
}

.auth-header h1 {
  font-size: 1.5rem;
}

.auth-header p {
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.btn-block {
  width: 100%;
  margin-top: 0.5rem;
}

.auth-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
}
</style>
