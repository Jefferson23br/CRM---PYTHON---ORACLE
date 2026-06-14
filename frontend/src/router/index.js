import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/registro',
      name: 'registro',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/recuperar-senha',
      name: 'recuperar-senha',
      component: () => import('@/views/auth/RecuperarSenhaView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'clientes',
          name: 'clientes',
          component: () => import('@/views/clientes/ClientesView.vue'),
        },
        {
          path: 'usuarios',
          name: 'usuarios',
          component: () => import('@/views/usuarios/UsuariosView.vue'),
        },
        {
          path: 'topicos',
          name: 'topicos',
          component: () => import('@/views/topicos/TopicosView.vue'),
        },
        {
          path: 'topicos/:id',
          name: 'topico-detalhe',
          component: () => import('@/views/topicos/TopicoDetalheView.vue'),
        },
        {
          path: 'empresa',
          name: 'empresa',
          component: () => import('@/views/empresa/EmpresaView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const hasToken = auth.isAuthenticated

  if (to.meta.requiresAuth && !hasToken) {
    return { name: 'login', replace: true }
  }

  if (to.meta.guest && hasToken) {
    return { name: 'dashboard', replace: true }
  }

  if (hasToken && !auth.usuario && to.meta.requiresAuth) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { name: 'login', replace: true }
    }
  }
})

export default router
