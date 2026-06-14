import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref(null)
  const loading = ref(false)
  const accessToken = ref(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access, refresh) {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    accessToken.value = access
  }

  function clearSession() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    accessToken.value = null
    usuario.value = null
  }

  async function login(email, senha) {
    loading.value = true
    try {
      const { data } = await api.post('/auth/login', { email, senha })
      setTokens(data.access_token, data.refresh_token)
      usuario.value = data.usuario
      return data
    } finally {
      loading.value = false
    }
  }

  async function registro(empresa, usuarioData) {
    loading.value = true
    try {
      const { data } = await api.post('/auth/registro', {
        empresa,
        usuario: usuarioData,
      })
      setTokens(data.access_token, data.refresh_token)
      usuario.value = data.usuario
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!isAuthenticated.value) return null
    const { data } = await api.get('/auth/me')
    usuario.value = data
    return data
  }

  async function recuperarSenha(email) {
    const { data } = await api.post('/auth/recuperar-senha', { email })
    return data
  }

  function logout() {
    clearSession()
  }

  return {
    usuario,
    loading,
    isAuthenticated,
    login,
    registro,
    fetchMe,
    recuperarSenha,
    logout,
  }
})
