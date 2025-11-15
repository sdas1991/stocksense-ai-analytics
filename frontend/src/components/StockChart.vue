<template>
  <div class="card">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold">Price Chart</h3>
      <div class="flex space-x-2">
        <button
          v-for="period in periods"
          :key="period"
          @click="$emit('period-change', period)"
          class="px-3 py-1 text-sm rounded"
          :class="selectedPeriod === period
            ? 'bg-primary-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
        >
          {{ period.toUpperCase() }}
        </button>
      </div>
    </div>
    <div v-if="chartData" class="h-80">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="h-80 flex items-center justify-center text-gray-400">
      No chart data available
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  historicalData: {
    type: Array,
    default: () => []
  },
  selectedPeriod: {
    type: String,
    default: '1mo'
  }
})

defineEmits(['period-change'])

const periods = ['1mo', '3mo', '6mo', '1y']

const chartData = computed(() => {
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
        label: 'Close Price',
        data: props.historicalData.map(d => d.close),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      },
      {
        label: 'EMA 12',
        data: props.historicalData.map(d => d.ema_short),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [5, 5],
        pointRadius: 0
      },
      {
        label: 'EMA 50',
        data: props.historicalData.map(d => d.ema_long),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [5, 5],
        pointRadius: 0
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || ''
          if (label) {
            label += ': '
          }
          if (context.parsed.y !== null) {
            label += '$' + context.parsed.y.toFixed(2)
          }
          return label
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: false,
      ticks: {
        callback: function(value) {
          return '$' + value.toFixed(2)
        }
      }
    }
  }
}
</script>
