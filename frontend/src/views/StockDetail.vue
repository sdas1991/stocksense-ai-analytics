<template>
  <div class="px-4 py-6">
    <button
      @click="$router.back()"
      class="mb-4 text-primary-600 hover:text-primary-700 flex items-center"
    >
      <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back
    </button>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading stock details...</p>
      </div>
    </div>

    <div v-else-if="stockData">
      <StockSummaryCard :stock="stockData" />
    </div>

    <div v-else class="card text-center py-12">
      <p class="text-gray-500">Stock not found</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { stockApi } from '../services/api'
import StockSummaryCard from '../components/StockSummaryCard.vue'

const route = useRoute()
const loading = ref(false)
const stockData = ref(null)

onMounted(async () => {
  const symbol = route.params.symbol
  if (symbol) {
    await loadStock(symbol)
  }
})

const loadStock = async (symbol) => {
  try {
    loading.value = true
    const response = await stockApi.analyzeStock(symbol)
    stockData.value = response.data
  } catch (error) {
    console.error('Error loading stock:', error)
  } finally {
    loading.value = false
  }
}
</script>
