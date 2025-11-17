<template>
  <div class="card">
    <h2 class="text-xl font-bold mb-4">Market Overview</h2>

    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-2 text-gray-500">Loading market data...</p>
    </div>

    <div v-else-if="overview">
      <!-- Major Indices -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div
          v-for="(data, symbol) in overview.indices"
          :key="symbol"
          class="p-4 bg-gray-50 rounded-lg"
        >
          <p class="text-sm text-gray-500">{{ getIndexName(symbol) }}</p>
          <p class="text-2xl font-bold text-gray-900">
            {{ data.price ? data.price.toFixed(2) : 'N/A' }}
          </p>
          <p
            class="text-sm font-medium"
            :class="data.change_percent >= 0 ? 'text-green-600' : 'text-red-600'"
          >
            {{ data.change_percent >= 0 ? '+' : '' }}{{ data.change_percent ? data.change_percent.toFixed(2) : '0.00' }}%
          </p>
        </div>
      </div>

      <!-- Top Movers -->
      <div v-if="overview.movers" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Top Gainers -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-green-700">
            Top Gainers
          </h3>
          <div class="space-y-2">
            <div
              v-for="stock in overview.movers.top_gainers"
              :key="stock.symbol"
              class="flex justify-between items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 cursor-pointer transition"
              @click="$emit('select-stock', stock.symbol)"
            >
              <div>
                <p class="font-semibold text-gray-900">{{ stock.symbol }}</p>
                <p class="text-xs text-gray-600">{{ stock.companyName || stock.name }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">
                  ${{ (stock.latestPrice || stock.price || 0).toFixed(2) }}
                </p>
                <p class="text-sm font-semibold text-green-600">
                  +{{ (stock.changePercent || stock.change_percent || 0).toFixed(2) }}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Losers -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-red-700">
            Top Losers
          </h3>
          <div class="space-y-2">
            <div
              v-for="stock in overview.movers.top_losers"
              :key="stock.symbol"
              class="flex justify-between items-center p-3 bg-red-50 rounded-lg hover:bg-red-100 cursor-pointer transition"
              @click="$emit('select-stock', stock.symbol)"
            >
              <div>
                <p class="font-semibold text-gray-900">{{ stock.symbol }}</p>
                <p class="text-xs text-gray-600">{{ stock.companyName || stock.name }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">
                  ${{ (stock.latestPrice || stock.price || 0).toFixed(2) }}
                </p>
                <p class="text-sm font-semibold text-red-600">
                  {{ (stock.changePercent || stock.change_percent || 0).toFixed(2) }}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Last Updated -->
      <div class="mt-4 text-xs text-gray-500 text-center">
        Last updated: {{ formatTime(overview.timestamp) }}
      </div>
    </div>

    <div v-else class="text-center py-8 text-gray-500">
      No market data available
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { stockApi } from '../services/api'

const emit = defineEmits(['select-stock'])

const loading = ref(false)
const overview = ref(null)

const indexNames = {
  'SPY': 'S&P 500',
  'QQQ': 'NASDAQ',
  'DIA': 'Dow Jones',
  '^VIX': 'VIX'
}

const getIndexName = (symbol) => {
  return indexNames[symbol] || symbol
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

const loadOverview = async () => {
  try {
    loading.value = true
    const response = await stockApi.getMarketOverview()
    overview.value = response.data
  } catch (error) {
    console.error('Error loading market overview:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOverview()
  // Refresh every 5 minutes
  setInterval(loadOverview, 300000)
})

defineExpose({ loadOverview })
</script>
