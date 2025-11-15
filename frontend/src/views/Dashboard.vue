<template>
  <div class="px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Stock Analysis Dashboard</h1>
      <p class="text-gray-600">Search for stocks and get AI-powered technical analysis</p>
    </div>

    <div class="mb-8">
      <StockSearch
        ref="searchRef"
        @search="handleSearch"
      />
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Analyzing stock data...</p>
      </div>
    </div>

    <div v-else-if="stockData">
      <div class="mb-6">
        <StockSummaryCard :stock="stockData" />
      </div>

      <div class="mb-6">
        <StockChart
          :historical-data="historicalData"
          :selected-period="selectedPeriod"
          @period-change="handlePeriodChange"
        />
      </div>

      <div class="mb-6">
        <IndicatorsChart :historical-data="historicalData" />
      </div>

      <div class="flex justify-center">
        <button
          @click="addToWatchlist"
          :disabled="addingToWatchlist"
          class="btn btn-primary"
        >
          {{ addingToWatchlist ? 'Adding...' : 'Add to Watchlist' }}
        </button>
      </div>
    </div>

    <div v-else class="card text-center py-12">
      <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">No stock selected</h3>
      <p class="mt-2 text-gray-500">Enter a stock symbol above to get started</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { stockApi } from '../services/api'
import StockSearch from '../components/StockSearch.vue'
import StockSummaryCard from '../components/StockSummaryCard.vue'
import StockChart from '../components/StockChart.vue'
import IndicatorsChart from '../components/IndicatorsChart.vue'

const searchRef = ref(null)
const loading = ref(false)
const stockData = ref(null)
const historicalData = ref([])
const selectedPeriod = ref('1mo')
const addingToWatchlist = ref(false)

const handleSearch = async (symbol) => {
  try {
    loading.value = true
    searchRef.value?.setLoading(true)
    searchRef.value?.setError('')
    stockData.value = null
    historicalData.value = []

    // Fetch stock analysis
    const analysisResponse = await stockApi.analyzeStock(symbol, selectedPeriod.value)
    stockData.value = analysisResponse.data

    // Fetch historical data
    const historyResponse = await stockApi.getStockHistory(symbol, selectedPeriod.value)
    historicalData.value = historyResponse.data.data

  } catch (error) {
    console.error('Error fetching stock data:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to fetch stock data. Please try again.'
    searchRef.value?.setError(errorMsg)
  } finally {
    loading.value = false
    searchRef.value?.setLoading(false)
  }
}

const handlePeriodChange = async (period) => {
  if (!stockData.value) return

  selectedPeriod.value = period
  await handleSearch(stockData.value.symbol)
}

const addToWatchlist = async () => {
  if (!stockData.value) return

  try {
    addingToWatchlist.value = true
    await stockApi.addToWatchlist(stockData.value.symbol)
    alert(`${stockData.value.symbol} added to watchlist!`)
  } catch (error) {
    console.error('Error adding to watchlist:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to add to watchlist'
    alert(errorMsg)
  } finally {
    addingToWatchlist.value = false
  }
}
</script>
