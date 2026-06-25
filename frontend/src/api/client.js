import axios from 'axios'

const API_ORIGIN = import.meta.env.VITE_API_URL || ''
const api = axios.create({
  baseURL: API_ORIGIN ? `${API_ORIGIN.replace(/\/$/, '')}/api` : '/api',
  timeout: 120_000, // 2 min — real-mode ONNX inference may be slow on first load
})

export async function getSamples() {
  const { data } = await api.get('/samples')
  return data
}

export async function analyze({ mode, sampleId, image, clinical }) {
  const form = new FormData()
  form.append('mode', mode)
  if (sampleId) form.append('sample_id', sampleId)
  if (image) form.append('image', image)
  if (clinical) {
    for (const [k, v] of Object.entries(clinical)) {
      if (v !== '' && v != null) form.append(k, v)
    }
  }
  const { data } = await api.post('/analyze', form)
  return data
}

/**
 * Extract a human-readable error message from an Axios error.
 * Handles: backend detail, validation errors, network failures, timeouts.
 */
export function extractErrorMessage(err) {
  // 1. Backend returned a JSON { detail: "..." }
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail

  // 2. FastAPI validation error array  { detail: [{ msg, loc, type }] }
  if (Array.isArray(detail)) {
    return detail
      .map((e) => `${(e.loc || []).join(' → ')}: ${e.msg}`)
      .join('; ')
  }

  // 3. HTTP status but no structured detail
  if (err.response) {
    const status = err.response.status
    if (status === 413) return 'Image file is too large (max 4 MB)'
    if (status === 422) return 'Invalid input — please check the clinical data fields'
    if (status === 503) return 'Vision model is unavailable — model files may be missing'
    return `Server error (HTTP ${status})`
  }

  // 4. Network / timeout errors (no response received)
  if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
    return 'Request timed out — the model may still be loading. Please try again.'
  }
  if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
    return 'Cannot reach the backend server. Is it running?'
  }

  // 5. Fallback
  return err.message || 'Analysis failed — unknown error'
}
