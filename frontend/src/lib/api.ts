import axios from 'axios'
import type {
  AdminSummary,
  DemoCredentials,
  Product,
  ProductUploadResponse,
  RecommendationResponse,
  SizeChart,
  TokenResponse,
  User,
} from '../types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 12000,
})

export function authHeader(token: string | null) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams()
  body.append('username', email)
  body.append('password', password)
  const response = await api.post<TokenResponse>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}

export async function me(token: string): Promise<User> {
  const response = await api.get<User>('/me', { headers: authHeader(token) })
  return response.data
}

export async function demoCredentials(): Promise<DemoCredentials> {
  const response = await api.get<DemoCredentials>('/demo/credentials')
  return response.data
}

export async function listProducts(token: string): Promise<Product[]> {
  const response = await api.get<Product[]>('/products', { headers: authHeader(token) })
  return response.data
}

export async function fetchChart(token: string, productId: string): Promise<SizeChart> {
  const response = await api.get<{ chart: SizeChart }>(`/chart/${productId}`, { headers: authHeader(token) })
  return response.data.chart
}

export async function uploadProduct(token: string, formData: FormData): Promise<ProductUploadResponse> {
  const response = await api.post<ProductUploadResponse>('/upload-product', formData, {
    headers: {
      ...authHeader(token),
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function generateChart(token: string, productId: string): Promise<SizeChart> {
  const response = await api.post<{ chart: SizeChart }>(
    '/generate-chart',
    { product_id: productId },
    { headers: authHeader(token) },
  )
  return response.data.chart
}

export async function recommendSize(token: string, payload: Record<string, unknown>): Promise<RecommendationResponse> {
  const response = await api.post<RecommendationResponse>('/recommend-size', payload, {
    headers: authHeader(token),
  })
  return response.data
}

export async function submitFeedback(token: string, payload: Record<string, unknown>) {
  const response = await api.post('/feedback', payload, { headers: authHeader(token) })
  return response.data
}

export async function adminSummary(token: string): Promise<AdminSummary> {
  const response = await api.get<AdminSummary>('/admin/summary', { headers: authHeader(token) })
  return response.data
}
