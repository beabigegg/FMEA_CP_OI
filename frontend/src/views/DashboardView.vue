<template>
  <div>
    <el-page-header @back="handleLogout">
      <template #content>
        <span class="text-large font-600 mr-3"> Welcome, {{ authStore.username }} </span>
      </template>
      <template #extra>
        <el-button type="primary" @click="handleLogout">Logout</el-button>
      </template>
    </el-page-header>

    <el-divider />

    <div class="main-content">
      <!-- Document Upload Section -->
      <el-card class="upload-card">
        <template #header>
          <span>Upload New Document</span>
        </template>
        <el-form :model="uploadForm" label-width="120px">
          <el-form-item label="Document Type">
            <el-radio-group v-model="uploadForm.document_type">
              <el-radio label="FMEA" />
              <el-radio label="CP" />
            </el-radio-group>
          </el-form-item>
          <el-form-item label="Select File">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              :on-change="handleFileChange"
              action="/api/v1/documents/upload"
            >
              <template #trigger>
                <el-button type="primary">Select file</el-button>
              </template>
              <el-button class="ml-3" type="success" @click="submitUpload" :loading="uploading">
                Upload to server
              </el-button>
            </el-upload>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Document List Section -->
      <el-card class="list-card">
        <template #header>
          <span>Uploaded Documents</span>
        </template>
        <el-table :data="documents" v-loading="loadingDocuments" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="file_name" label="File Name" />
          <el-table-column prop="document_type" label="Type" width="100" />
          <el-table-column prop="uploaded_by" label="Uploaded By" />
          <el-table-column prop="created_at" label="Upload Time" />
          <el-table-column label="Actions" width="120">
            <template #default="scope">
              <el-button size="small" @click="viewDocument(scope.row.id)">View</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import { ElNotification } from 'element-plus'

// --- State and Refs ---
const authStore = useAuthStore()
const router = useRouter()
const documents = ref([])
const loadingDocuments = ref(false)
const uploadRef = ref()
const uploading = ref(false)
const uploadForm = ref({
  document_type: 'FMEA',
  file: null
})

// --- Logic ---
function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

async function fetchDocuments() {
  loadingDocuments.value = true
  try {
    const response = await axios.get('/api/v1/documents')
    documents.value = response.data
  } catch (error) {
    ElNotification({
      title: 'Error',
      message: 'Failed to fetch documents.',
      type: 'error',
    })
  } finally {
    loadingDocuments.value = false
  }
}

function handleFileChange(file) {
  uploadForm.value.file = file.raw
}

async function submitUpload() {
  if (!uploadForm.value.file) {
    ElNotification({ title: 'Warning', message: 'Please select a file first.', type: 'warning' })
    return
  }

  uploading.value = true
  const formData = new FormData()
  formData.append('file', uploadForm.value.file)
  formData.append('document_type', uploadForm.value.document_type)

  try {
    await axios.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    ElNotification({ title: 'Success', message: 'File uploaded successfully!', type: 'success' })
    uploadRef.value.clearFiles() // Clear file list in upload component
    uploadForm.value.file = null
    fetchDocuments() // Refresh the document list
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Upload failed.'
    ElNotification({ title: 'Error', message: errorMessage, type: 'error' })
  } finally {
    uploading.value = false
  }
}

function viewDocument(id) {
  router.push({ name: 'document-detail', params: { id } })
}

// --- Lifecycle Hooks ---
onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.main-content {
  margin-top: 20px;
}
.upload-card {
  margin-bottom: 20px;
}
.ml-3 {
  margin-left: 10px;
}
</style>