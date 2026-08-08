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

export async function listProducts(): Promise<Product[]> {
  const response = await api.get<Product[]>('/products')
  return response.data
}

export async function createProduct(formData: FormData): Promise<ProductCreateResponse> {
  const response = await api.post<ProductCreateResponse>('/products', formData)
  return response.data
}

export async function recommendSize(payload: RecommendationRequest): Promise<RecommendationResponse> {
  const response = await api.post<RecommendationResponse>('/recommend', payload)
  return response.data
}
