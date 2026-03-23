import axios from 'axios'

// Create axios instance
const service = axios.create({
      baseURL: '',
  timeout: 300000, // 5minutesTimeout（OntologyGenerateMayRequiresLongTime）
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor（fault-tolerant retry mechanism）
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // IfBackstatus codeis notsuccess，throwError
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)
    
    // ProcessTimeout
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }
    
    // ProcessNetworkError
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

// with retryRequest
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
