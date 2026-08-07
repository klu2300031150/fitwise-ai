export type UserRole = 'seller' | 'customer' | 'admin'

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type User = {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export type FabricDetails = {
  fabric_type: string
  gsm?: number | null
  stretch_percentage?: number | null
  weave_type?: string | null
}

export type SizeCell = {
  size: string
  chest: number
  waist: number
  hip: number
  sleeve: number
  length: number
  shoulder: number
  confidence: number
  notes: string[]
}

export type SizeChart = {
  id: string
  product_id: string
  sizes: SizeCell[]
  notes: string[]
  validation: Record<string, unknown>
  created_at: string
}

export type Product = {
  id: string
  seller_id: string
  name: string
  category: string
  front_image_path?: string | null
  back_image_path?: string | null
  flat_lay_image_path?: string | null
  tech_pack_path?: string | null
  status: string
  extracted_text?: string | null
  validation_summary?: { alerts?: string[] } | null
  chart_summary?: Record<string, unknown> | null
  created_at: string
}

export type ProductUploadResponse = {
  product: Product
  fabric: FabricDetails
  measurements: Record<string, number>
  chart: SizeChart
  explainability: Record<string, unknown>
}

export type RecommendationResponse = {
  recommendation_id: string
  product_id: string
  recommended_size: string
  confidence_score: number
  explanation: string[]
  cache_hit: boolean
  size_table: SizeCell[]
}

export type AdminSummary = {
  total_products: number
  total_recommendations: number
  cache_hit_rate: number
  validation_alerts: string[]
  top_sizing_trends: Array<{ size: string; count: number }>
}

export type DemoCredentials = {
  accounts: Array<{ email: string; password: string; role: UserRole }>
}
