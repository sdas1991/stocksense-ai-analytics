<template>
  <div class="px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">My Watchlist</h1>
      <p class="text-gray-600">Track your favorite stocks</p>
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading watchlist...</p>
      </div>
    </div>

    <div v-else-if="watchlist.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="item in watchlist"
        :key="item.symbol"
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="viewStock(item.symbol)"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-bold text-gray-900">{{ item.symbol }}</h3>
            <p v-if="item.notes" class="text-sm text-gray-500">{{ item.notes }}</p>
          </div>
          <button
            @click.stop="removeFromWatchlist(item.symbol)"
            class="text-red-500 hover:text-red-700"
            title="Remove from watchlist"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="item.last_price" class="space-y-2">
          <div>
            <p class="text-sm text-gray-500">Price</p>
            <p class="text-2xl font-bold text-gray-900">${{ item.last_price.toFixed(2) }}</p>
          </div>
          <div v-if="item.price_change_percent !== null">
            <p class="text-sm text-gray-500">Change</p>
            <p
              class="text-lg font-semibold"
              :class="item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'"
            >
              {{ item.price_change_percent >= 0 ? '+' : '' }}{{ item.price_change_percent.toFixed(2) }}%
            </p>
          </div>
          <div v-if="item.trend" class="flex items-center space-x-2">
            <span class="badge" :class="getTrendClass(item.trend)">
              {{ item.trend }}
            </span>
            <span v-if="item.recommendation" class="badge" :class="getRecommendationClass(item.recommendation)">
              {{ item.recommendation }}
            </span>
          </div>
        </div>

        <div v-else class="text-sm text-gray-400">
          No data available - Click to analyze
        </div>
      </div>
    </div>

    <div v-else class="card text-center py-12">
      <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">No stocks in watchlist</h3>
      <p class="mt-2 text-gray-500">Add stocks from the dashboard to track them here</p>
      <router-link to="/" class="mt-4 inline-block btn btn-primary">
        Go to Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stockApi } from '../services/api'

const router = useRouter()
const loading = ref(false)
const watchlist = ref([])

onMounted(async () => {
  await loadWatchlist()
})

const loadWatchlist = async () => {
  try {
    loading.value = true
    const response = await stockApi.getWatchlist()
    watchlist.value = response.data.watchlist
  } catch (error) {
    console.error('Error loading watchlist:', error)
  } finally {
    loading.value = false
  }
}

const viewStock = (symbol) => {
  router.push(`/stock/${symbol}`)
}

const removeFromWatchlist = async (symbol) => {
  if (!confirm(`Remove ${symbol} from watchlist?`)) {
    return
  }

  try {
    await stockApi.removeFromWatchlist(symbol)
    watchlist.value = watchlist.value.filter(item => item.symbol !== symbol)
  } catch (error) {
    console.error('Error removing from watchlist:', error)
    alert('Failed to remove from watchlist')
  }
}

const getTrendClass = (trend) => {
  switch (trend) {
    case 'Bullish':
      return 'badge-success'
    case 'Bearish':
      return 'badge-danger'
    default:
      return 'badge-neutral'
  }
}

const getRecommendationClass = (recommendation) => {
  switch (recommendation) {
    case 'Buy':
      return 'badge-success'
    case 'Sell':
      return 'badge-danger'
    default:
      return 'badge-warning'
  }
}
</script>
