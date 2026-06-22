import axios from 'axios'

const API_ORIGIN = import.meta.env.VITE_API_URL || 'https://bridge-ai-demo-jtjd.vercel.app'
const api = axios.create({
  baseURL: `${API_ORIGIN.replace(/\/$/, '')}/api`,
}) // local dev uses Vite proxy; production falls back to the deployed backend

export async function getSamples() {
  const { data } = await api.get('/samples')
  return data
}

// analyze รับได้ 2 แบบ: { sampleId } หรือ { image, clinical }
export async function analyze({ sampleId, image, clinical }) {
  const form = new FormData()
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
