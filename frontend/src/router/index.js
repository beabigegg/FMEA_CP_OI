import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// --- Route Components ---
// We will create these view components in the next steps
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true } // This route requires authentication
  },

  {
    path: '/documents/:id',
    name: 'document-detail',
    component: () => import('../views/DocumentDetailView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- Navigation Guard ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // If the route requires auth and the user is not authenticated,
    // redirect to the login page.
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    // If the user is authenticated and tries to visit the login page,
    // redirect them to the dashboard.
    next({ name: 'dashboard' })
  } else {
    // Otherwise, allow the navigation.
    next()
  }
})

export default router
