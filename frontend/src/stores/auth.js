import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const token = ref(localStorage.getItem('token') || null)
  const username = ref(localStorage.getItem('username') || null)

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value)

  // --- Actions ---
  async function login(usernameInput, passwordInput) {
    const response = await axios.post('/auth/token', new URLSearchParams({
      username: usernameInput,
      password: passwordInput
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    const accessToken = response.data.access_token
    token.value = accessToken
    username.value = usernameInput

    localStorage.setItem('token', accessToken)
    localStorage.setItem('username', usernameInput)

    // Set Axios default header for subsequent requests
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }

  function logout() {
    token.value = null
    username.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    delete axios.defaults.headers.common['Authorization']
  }

  // Check for token on initial load
  function init() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  init()

  return { token, username, isAuthenticated, login, logout }
})
