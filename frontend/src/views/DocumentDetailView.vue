<template>
  <div v-if="loading">
    <el-skeleton :rows="10" animated />
  </div>
  <div v-else-if="error">
    <el-result status="error" title="Error" :sub-title="error" />
  </div>
  <div v-else-if="document">
    <el-page-header @back="goBack">
      <template #content>
        <span>{{ document.file_name }}</span>
      </template>
      <template #extra>
        <el-button 
          type="primary"
          @click="saveAssociations"
          :disabled="!selectedFmeaItem || selectedCpItemIds.length === 0"
          :loading="savingAssociations"
        >
          Save Associations
        </el-button>
      </template>
    </el-page-header>
    <el-divider />

    <div class="workspace">
      <!-- FMEA Items Table -->
      <el-card class="table-card">
        <template #header>FMEA Items (Click a row to select)</template>
        <el-table 
          :data="document.fmea_items" 
          height="75vh" 
          border 
          stripe
          highlight-current-row
          @current-change="handleFmeaRowSelect"
        >
          <el-table-column prop="id" label="ID" width="70" fixed />
          <el-table-column prop="failure_mode" label="Failure Mode" width="250" />
          <el-table-column prop="failure_cause" label="Failure Cause" width="250" />
          <el-table-column prop="prevention_controls" label="Prevention Controls" width="220" />
          <el-table-column prop="detection_controls" label="Detection Controls" width="220" />
        </el-table>
      </el-card>

      <!-- Control Plan Items Table -->
      <el-card class="table-card">
        <template #header>
          <div class="cp-header">
            <span>Control Plan Items (Checkbox to associate)</span>
            <el-select 
              v-model="selectedCpDocId" 
              placeholder="Select a CP Document"
              @change="handleCpDocChange"
              filterable clearable
            >
              <el-option v-for="doc in cpDocumentList" :key="doc.id" :label="doc.file_name" :value="doc.id" />
            </el-select>
          </div>
        </template>
        <el-table 
          :data="cpItems" 
          v-loading="loadingCpItems || loadingAiSuggestions"
          height="70vh" 
          border 
          stripe
          ref="cpTableRef"
          :row-class-name="cpTableRowClassName"
          @selection-change="handleCpSelectionChange"
        >
          <el-table-column type="selection" width="55" fixed />
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="product_characteristic" label="Product Characteristic" width="250" />
          <el-table-column prop="control_method" label="Control Method" width="220" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElNotification } from 'element-plus'

// --- Router & Route ---
const route = useRoute()
const router = useRouter()
const documentId = route.params.id

// --- Component State ---
const document = ref(null)
const loading = ref(true)
const error = ref(null)
const cpDocumentList = ref([])
const selectedCpDocId = ref(null)
const cpItems = ref([])
const loadingCpItems = ref(false)
const loadingAiSuggestions = ref(false)
const savingAssociations = ref(false)

// --- Selection and Suggestion State ---
const selectedFmeaItem = ref(null)
const aiSuggestedCpIds = ref([])
const selectedCpItemIds = ref([])
const cpTableRef = ref() // Ref for the CP table component

// --- Methods ---
async function fetchInitialData() {
  loading.value = true
  try {
    const [mainDocResponse, allDocsResponse] = await Promise.all([
      axios.get(`/api/v1/documents/${documentId}`),
      axios.get('/api/v1/documents')
    ])
    document.value = mainDocResponse.data
    cpDocumentList.value = allDocsResponse.data.filter(doc => doc.document_type === 'CP')
  } catch (err) {
    handleError(err, 'Failed to load initial data.')
  } finally {
    loading.value = false
  }
}

async function handleCpDocChange(cpDocId) {
  if (!cpDocId) {
    cpItems.value = []
    return
  }
  loadingCpItems.value = true
  try {
    const response = await axios.get(`/api/v1/documents/${cpDocId}`)
    cpItems.value = response.data.items
  } catch (err) {
    handleError(err, 'Failed to load CP document items.')
  } finally {
    loadingCpItems.value = false
  }
}

async function handleFmeaRowSelect(fmeaItem) {
  if (!fmeaItem) {
    selectedFmeaItem.value = null
    aiSuggestedCpIds.value = []
    return
  }
  selectedFmeaItem.value = fmeaItem
  
  if (!selectedCpDocId.value) {
    ElNotification({ title: 'Info', message: 'Please select a CP document to get AI suggestions.', type: 'info' })
    return
  }

  loadingAiSuggestions.value = true
  aiSuggestedCpIds.value = []
  try {
    const response = await axios.post(`/api/v1/ai/suggest-association/${fmeaItem.id}`)
    aiSuggestedCpIds.value = response.data.suggestions.map(s => s.suggested_cp_item_id)
    ElNotification({ title: 'Success', message: 'AI suggestions loaded!', type: 'success' })
  } catch (err) {
    handleError(err, 'Failed to get AI suggestions.')
  } finally {
    loadingAiSuggestions.value = false
  }
}

function handleCpSelectionChange(selection) {
  selectedCpItemIds.value = selection.map(item => item.id)
}

async function saveAssociations() {
  if (!selectedFmeaItem.value || selectedCpItemIds.value.length === 0) {
    ElNotification({ title: 'Warning', message: 'Please select an FMEA item and at least one CP item.', type: 'warning' });
    return;
  }

  savingAssociations.value = true;
  try {
    const payload = {
      fmea_item_id: selectedFmeaItem.value.id,
      cp_item_ids: selectedCpItemIds.value
    };
    await axios.post('/api/v1/associations', payload);
    ElNotification({ title: 'Success', message: 'Associations have been saved successfully!', type: 'success' });
  } catch (err) {
    handleError(err, 'Failed to save associations.');
  } finally {
    savingAssociations.value = false;
  }
}

// --- UI Helpers ---
function cpTableRowClassName({ row }) {
  if (aiSuggestedCpIds.value.includes(row.id)) {
    return 'ai-suggestion-row'
  }
  return ''
}

function goBack() {
  router.push({ name: 'dashboard' })
}

function handleError(err, defaultMessage) {
  const message = err.response?.data?.detail || defaultMessage
  ElNotification({ title: 'Error', message, type: 'error' })
}

// --- Lifecycle ---
onMounted(() => {
  fetchInitialData()
});

</script>

<style>
/* Global style for AI suggestion highlight */
.el-table .ai-suggestion-row {
  --el-table-tr-bg-color: #e1f3d8; /* A light green color */
}

.workspace {
  display: flex;
  gap: 20px;
}
.table-card {
  flex: 1;
}
.cp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>