<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>FMEA-CP Platform Login</span>
        </div>
      </template>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="Username">
          <el-input v-model="username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">Login</el-button>
        </el-form-item>
      </el-form>
      <el-alert v-if="error" :title="error" type="error" show-icon />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const authStore = useAuthStore()
const router = useRouter()

async function handleLogin() {
  loading.value = true
  error.value = null
  try {
    await authStore.login(username.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.login-card {
  width: 400px;
}
</style>