<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const email = ref('')
const mensagem = ref('')
const erro = ref('')

async function enviar() {
  erro.value = ''
  mensagem.value = ''
  try {
    const data = await auth.recuperarSenha(email.value)
    mensagem.value = data.mensagem
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao enviar solicitação'
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <h1>Recuperar senha</h1>
        <p>Enviaremos instruções para o seu e-mail</p>
      </div>

      <div v-if="erro" class="alert alert-error">{{ erro }}</div>
      <div v-if="mensagem" class="alert alert-success">{{ mensagem }}</div>

      <form @submit.prevent="enviar">
        <div class="form-group">
          <label>E-mail</label>
          <input v-model="email" type="email" required />
        </div>
        <button type="submit" class="btn btn-primary btn-block">Enviar</button>
      </form>

      <div class="auth-links">
        <router-link to="/login">Voltar ao login</router-link>
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

.auth-header p {
  color: var(--color-text-muted);
}

.btn-block {
  width: 100%;
}

.auth-links {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
}
</style>
