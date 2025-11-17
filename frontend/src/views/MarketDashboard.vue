<template>
  <div class="px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Market Dashboard</h1>
      <p class="text-gray-600">Real-time market trends and top movers</p>
    </div>

    <!-- Market Overview -->
    <div class="mb-6">
      <MarketOverview
        ref="marketOverviewRef"
        @select-stock="handleSelectStock"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Market Movers (Full Width on Mobile, 2/3 on Desktop) -->
      <div class="lg:col-span-2">
        <div class="card">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Market Movers</h2>
            <button
              @click="loadMovers"
              class="btn btn-secondary btn-sm"
              :disabled="loadingMovers"
            >
              {{ loadingMovers ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>

          <div v-if="loadingMovers" class="text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>

          <div v-else-if="movers">
            <!-- Tabs -->
            <div class="flex border-b mb-4">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                class="px-4 py-2 font-medium transition-colors"
                :class="activeTab === tab.id
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-500 hover:text-gray-700'"
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="space-y-2">
              <div
                v-for="stock in currentTabData"
                :key="stock.symbol"
                class="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition"
                @click="handleSelectStock(stock.symbol)"
              >
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ stock.symbol }}</p>
                  <p class="text-sm text-gray-600">{{ stock.companyName || stock.name || 'N/A' }}</p>
                </div>
                <div class="text-right">
                  <p class="font-medium text-gray-900">
                    ${{ (stock.latestPrice || stock.price || 0).toFixed(2) }}
                  </p>
                  <p
                    class="text-sm font-semibold"
                    :class="getChangeColor(stock)"
                  >
                    {{ formatChange(stock) }}
                  </p>
                </div>
                <div class="ml-4">
                  <p class="text-xs text-gray-500">Vol</p>
                  <p class="text-sm font-medium text-gray-700">
                    {{ formatVolume(stock.latestVolume || stock.volume) }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            No market movers data available
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Provider Status -->
        <ProviderStatus />

        <!-- Quick Stats -->
        <div class="card">
          <h3 class="text-lg font-semibold mb-4">Quick Stats</h3>
          <div v-if="movers" class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Advancing</span>
              <span class="font-semibold text-green-600">
                {{ movers.gainers?.length || 0 }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Declining</span>
              <span class="font-semibold text-red-600">
                {{ movers.losers?.length || 0 }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Most Active</span>
              <span class="font-semibold text-blue-600">
                {{ movers.most_active?.length || 0 }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stockApi } from '../services/api'
import MarketOverview from '../components/MarketOverview.vue'
import ProviderStatus from '../components/ProviderStatus.vue'

const router = useRouter()

const marketOverviewRef = ref(null)
const loadingMovers = ref(false)
const movers = ref(null)
const activeTab = ref('gainers')

const tabs = [
  { id: 'gainers', label: 'Top Gainers' },
  { id: 'losers', label: 'Top Losers' },
  { id: 'active', label: 'Most Active' }
]

const currentTabData = computed(() => {
  if (!movers.value) return []

  switch (activeTab.value) {
    case 'gainers':
      return movers.value.gainers || []
    case 'losers':
      return movers.value.losers || []
    case 'active':
      return movers.value.most_active || []
    default:
      return []
  }
})

const getChangeColor = (stock) => {
  const change = stock.changePercent || stock.change_percent || 0
  return change >= 0 ? 'text-green-600' : 'text-red-600'
}

const formatChange = (stock) => {
  const change = stock.changePercent || stock.change_percent || 0
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const formatVolume = (volume) => {
  if (!volume) return 'N/A'
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(1) + 'M'
  } else if (volume >= 1000) {
    return (volume / 1000).toFixed(1) + 'K'
  }
  return volume.toString()
}

const loadMovers = async () => {
  try {
    loadingMovers.value = true
    const response = await stockApi.getMarketMovers()
    movers.value = response.data
  } catch (error) {
    console.error('Error loading market movers:', error)
  } finally {
    loadingMovers.value = false
  }
}

const handleSelectStock = (symbol) => {
  router.push(`/stock/${symbol}`)
}

onMounted(() => {
  loadMovers()
  // Refresh movers every 5 minutes
  setInterval(loadMovers, 300000)
})
</script>
