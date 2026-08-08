import axios from 'axios'
import type {
  Product,
  ProductCreateResponse,
  RecommendationRequest,
  RecommendationResponse,
} from '../types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 12000,
})

// Ensure FormData requests don't carry an explicit Content-Type header
// so the browser can add the multipart boundary automatically.
api.interceptors.request.use((config) => {
  try {
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      if (config.headers) {
        // Remove explicit Content-Type to let the browser set boundary
        delete (config.headers as any)['Content-Type']
      }
    }
  } catch (e) {
    // ignore
  }
  return config
})

export async function listProducts(): Promise<Product[]> {
  const response = await api.get<Product[]>('/products')
  return response.data
}

export async function createProduct(formData: FormData): Promise<ProductCreateResponse> {
  const response = await api.post<ProductCreateResponse>('/products', formData)
  return response.data
}

export async function deleteProduct(productId: string): Promise<void> {
  await api.delete(`/products/${productId}`)
}

export async function recommendSize(payload: RecommendationRequest): Promise<RecommendationResponse> {
  const response = await api.post<RecommendationResponse>('/recommend', payload)
  return response.data
}
