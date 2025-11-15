<template>
  <div class="stock-search">
    <div class="relative">
      <input
        v-model="searchSymbol"
        @keyup.enter="handleSearch"
        type="text"
        placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)..."
        class="w-full px-4 py-3 pl-12 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      />
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <button
        @click="handleSearch"
        :disabled="!searchSymbol || loading"
        class="absolute inset-y-0 right-0 px-6 m-1 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {{ loading ? 'Analyzing...' : 'Analyze' }}
      </button>
    </div>
    <div v-if="error" class="mt-2 text-red-600 text-sm">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['search'])

const searchSymbol = ref('')
const loading = ref(false)
const error = ref('')

const handleSearch = () => {
  if (!searchSymbol.value.trim()) {
    error.value = 'Please enter a stock symbol'
    return
  }

  error.value = ''
  emit('search', searchSymbol.value.toUpperCase())
}

defineExpose({
  setLoading: (val) => { loading.value = val },
  setError: (msg) => { error.value = msg }
})
</script>
