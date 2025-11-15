<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- RSI Chart -->
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">RSI (Relative Strength Index)</h3>
      <div class="h-48">
        <Line v-if="rsiData" :data="rsiData" :options="rsiOptions" />
      </div>
    </div>

    <!-- MACD Chart -->
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">MACD</h3>
      <div class="h-48">
        <Line v-if="macdData" :data="macdData" :options="macdOptions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'

const props = defineProps({
  historicalData: {
    type: Array,
    default: () => []
  }
})

const rsiData = computed(() => {
  if (!props.historicalData || props.historicalData.length === 0) {
    return null
  }

  const labels = props.historicalData.map(d => {
    const date = new Date(d.date)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  return {
    labels,
    datasets: [
      {
        label: 'RSI',
        data: props.historicalData.map(d => d.rsi),
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const rsiOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    annotation: {
      annotations: {
        line1: {
          type: 'line',
          yMin: 70,
          yMax: 70,
          borderColor: 'rgb(239, 68, 68)',
          borderWidth: 1,
          borderDash: [5, 5],
        },
        line2: {
          type: 'line',
          yMin: 30,
          yMax: 30,
          borderColor: 'rgb(16, 185, 129)',
          borderWidth: 1,
          borderDash: [5, 5],
        }
      }
    }
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: {
        callback: function(value) {
          return value
        }
      }
    }
  }
}

const macdData = computed(() => {
  if (!props.historicalData || props.historicalData.length === 0) {
    return null
  }

  const labels = props.historicalData.map(d => {
    const date = new Date(d.date)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  return {
    labels,
    datasets: [
      {
        label: 'MACD',
        data: props.historicalData.map(d => d.macd),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'transparent',
        borderWidth: 2,
        tension: 0.4
      }
    ]
  }
})

const macdOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: false
    }
  }
}
</script>
