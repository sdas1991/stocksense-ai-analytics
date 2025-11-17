<template>
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">Data Providers Status</h3>

    <div v-if="loading" class="text-center py-4">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <div v-else-if="providers" class="space-y-2">
      <div
        v-for="(status, name) in providers"
        :key="name"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
      >
        <div class="flex items-center space-x-3">
          <div
            class="w-3 h-3 rounded-full"
            :class="status.available ? 'bg-green-500' : 'bg-gray-300'"
          ></div>
          <div>
            <p class="font-medium text-gray-900">{{ status.name }}</p>
            <p class="text-xs text-gray-500">
              {{ status.requires_key ? 'Requires API Key' : 'Free' }}
              <span v-if="status.rate_limit">
                • {{ status.rate_limit }} req/min
              </span>
            </p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-xs text-gray-600">
            {{ status.requests_made_last_minute || 0 }} requests
          </p>
          <span
            v-if="status.available"
            class="badge"
            :class="status.can_request ? 'badge-success' : 'badge-warning'"
          >
            {{ status.can_request ? 'Ready' : 'Throttled' }}
          </span>
          <span v-else class="badge badge-neutral">
            Unavailable
          </span>
        </div>
      </div>
    </div>

    <button
      @click="loadStatus"
      class="mt-4 w-full btn btn-secondary text-sm"
    >
      Refresh Status
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { stockApi } from '../services/api'

const loading = ref(false)
const providers = ref(null)

const loadStatus = async () => {
  try {
    loading.value = true
    const response = await stockApi.getProvidersStatus()
    providers.value = response.data.providers
  } catch (error) {
    console.error('Error loading provider status:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStatus()
})
</script>
