<template>
  <div class="card">
    <div class="flex justify-between items-start mb-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{ stock.symbol }}</h2>
        <p class="text-sm text-gray-500">{{ stock.company_name || stock.symbol }}</p>
        <p v-if="stock.sector" class="text-xs text-gray-400">{{ stock.sector }}</p>
      </div>
      <span
        class="badge text-lg px-4 py-2"
        :class="trendBadgeClass"
      >
        {{ stock.trend }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-4">
      <div>
        <p class="text-sm text-gray-500">Current Price</p>
        <p class="text-3xl font-bold text-gray-900">
          ${{ stock.close.toFixed(2) }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Change</p>
        <p
          class="text-2xl font-semibold"
          :class="stock.price_change >= 0 ? 'text-green-600' : 'text-red-600'"
        >
          {{ stock.price_change >= 0 ? '+' : '' }}{{ stock.price_change.toFixed(2) }}
          ({{ stock.price_change_percent >= 0 ? '+' : '' }}{{ stock.price_change_percent.toFixed(2) }}%)
        </p>
      </div>
    </div>

    <div class="border-t pt-4">
      <h3 class="text-lg font-semibold mb-2">Technical Indicators</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-xs text-gray-500">RSI</p>
          <p class="text-lg font-medium">{{ stock.rsi.toFixed(2) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500">MACD</p>
          <p class="text-lg font-medium">{{ stock.macd.toFixed(4) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500">EMA 12</p>
          <p class="text-lg font-medium">${{ stock.ema_12.toFixed(2) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500">EMA 50</p>
          <p class="text-lg font-medium">${{ stock.ema_50.toFixed(2) }}</p>
        </div>
      </div>
    </div>

    <div class="mt-4 p-4 bg-gradient-to-r rounded-lg"
         :class="recommendationGradient">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-white opacity-90">AI Recommendation</p>
          <p class="text-2xl font-bold text-white">{{ stock.recommendation }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm font-medium text-white opacity-90">Confidence</p>
          <p class="text-2xl font-bold text-white">{{ stock.confidence_score.toFixed(0) }}%</p>
        </div>
      </div>
    </div>

    <div v-if="stock.ai_summary" class="mt-4 p-4 bg-blue-50 rounded-lg">
      <h4 class="text-sm font-semibold text-blue-900 mb-2">AI Analysis</h4>
      <p class="text-sm text-blue-800">{{ stock.ai_summary }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stock: {
    type: Object,
    required: true
  }
})

const trendBadgeClass = computed(() => {
  switch (props.stock.trend) {
    case 'Bullish':
      return 'badge-success'
    case 'Bearish':
      return 'badge-danger'
    default:
      return 'badge-neutral'
  }
})

const recommendationGradient = computed(() => {
  switch (props.stock.recommendation) {
    case 'Buy':
      return 'from-green-500 to-green-600'
    case 'Sell':
      return 'from-red-500 to-red-600'
    default:
      return 'from-gray-500 to-gray-600'
  }
})
</script>
