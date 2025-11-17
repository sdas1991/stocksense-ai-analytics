import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data)
    } else if (error.request) {
      console.error('Network Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export const stockApi = {
  // Analyze stock
  analyzeStock: (symbol, period = '1y') => {
    return api.get(`/api/stock/${symbol}/analyze`, {
      params: { period }
    })
  },

  // Get stock history
  getStockHistory: (symbol, period = '1y') => {
    return api.get(`/api/stock/${symbol}/history`, {
      params: { period }
    })
  },

  // Get stock summary
  getStockSummary: (symbol) => {
    return api.get(`/api/stock/${symbol}/summary`)
  },

  // Get stock quote (real-time)
  getStockQuote: (symbol) => {
    return api.get(`/api/stock/${symbol}/quote`)
  },

  // Get company news
  getCompanyNews: (symbol, days = 7) => {
    return api.get(`/api/stock/${symbol}/news`, {
      params: { days }
    })
  },

  // Get trends
  getTrends: () => {
    return api.get('/api/trends')
  },

  // Market endpoints
  getMarketMovers: () => {
    return api.get('/api/market/movers')
  },

  getMarketOverview: () => {
    return api.get('/api/market/overview')
  },

  // Search symbols
  searchSymbols: (query) => {
    return api.get(`/api/search/${query}`)
  },

  // Data providers status
  getProvidersStatus: () => {
    return api.get('/api/providers/status')
  },

  // Get watchlist
  getWatchlist: () => {
    return api.get('/api/watchlist')
  },

  // Add to watchlist
  addToWatchlist: (symbol, notes = '') => {
    return api.post('/api/watchlist', { symbol, notes })
  },

  // Remove from watchlist
  removeFromWatchlist: (symbol) => {
    return api.delete(`/api/watchlist/${symbol}`)
  },

  // Health check
  healthCheck: () => {
    return api.get('/api/health')
  }
}

export default api
