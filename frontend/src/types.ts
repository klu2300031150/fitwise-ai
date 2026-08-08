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
  name: string
  category: string
  fabric_type: string
  gsm?: number | null
  stretch_percentage?: number | null
  weave_type?: string | null
  front_image_path?: string | null
  back_image_path?: string | null
  flat_lay_image_path?: string | null
  tech_pack_path?: string | null
  tech_pack_text?: string | null
  chart: SizeChart
  explanation: string[]
  created_at: string
}

export type ProductCreateResponse = {
  message: string
  product: Product
  chart: SizeChart
  explanation: string[]
}

export type RecommendationRequest = {
  product_id: string
  height: number | null
  weight: number | null
  chest: number
  waist: number
  hip: number
}

export type RecommendationResponse = {
  product_id: string
  recommended_size: string
  confidence_score: number
  reason: string[]
  size_table: SizeCell[]
}
